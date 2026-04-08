"""
=========================================================================
 AURA — FULL END-TO-END SYSTEM TEST SUITE
 Author : QA Engineering
 Date   : 2026-04-08
 Purpose: Validate the entire sensor→API pipeline with extreme prejudice.
=========================================================================
"""

import sys, os, time, math, random, json, copy, threading
from collections import Counter
from typing import List, Dict, Tuple, Optional

sys.path.insert(0, os.path.dirname(__file__))

# ── Imports under test ──────────────────────────────────────────────────
from config import (
    GRID_WIDTH, GRID_HEIGHT,
    RISK_TEMP_HIGH, RISK_TEMP_MEDIUM,
    RISK_GAS_HIGH, RISK_GAS_MEDIUM,
    COST_SAFE, COST_MEDIUM, COST_HIGH,
    PROB_SAFE, PROB_MEDIUM, PROB_HIGH,
    SURVIVOR_DIST_THRESHOLD, SURVIVOR_TIME_THRESHOLD,
    BASE_STATION_X, BASE_STATION_Y,
)
from detection.hazard import classify_risk, risk_to_cost
from detection.survivor import detect_survivor
from detection.duplicate import is_duplicate
from database.victim_db import VictimDB
from mapping.grid_map import GridMap
from planning.pathfinding import a_star, heuristic
from data.simulator import generate_sensor_data, SensorSimulator
from utils.helpers import (
    ValidationError, normalize_location, normalize_sensor_payload,
    calculate_distance,
)

# ── Globals ─────────────────────────────────────────────────────────────
PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"
WARN = "\033[93m⚠  WARN\033[0m"
BUGS: List[str] = []
SUGGESTIONS: List[str] = []

results: Dict[str, str] = {}

def record(module: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    results[module] = status
    tag = PASS if passed else FAIL
    print(f"  {tag}  {module}" + (f" — {detail}" if detail else ""))
    if not passed and detail:
        BUGS.append(f"[{module}] {detail}")


# =====================================================================
#  STEP 1 — SIMULATE 30 SEQUENTIAL SENSOR INPUTS
# =====================================================================
def step1_simulate_data_stream() -> List[Dict]:
    """Generate 30 controlled sensor packets."""
    print("\n" + "=" * 70)
    print("  STEP 1 — SIMULATE DATA STREAM (30 sensor packets)")
    print("=" * 70)

    random.seed(42)  # Reproducible
    packets = []
    for i in range(30):
        pkt = {
            "drone_id": random.randint(1, 4),
            "temperature": round(random.uniform(20, 100), 2),
            "gas_level": round(random.uniform(10, 100), 2),
            "location": [random.randint(0, 49), random.randint(0, 49)],
            "timestamp": time.time() + i,  # sequential timestamps
        }
        packets.append(pkt)
    print(f"  Generated {len(packets)} packets across drones {set(p['drone_id'] for p in packets)}")
    print(f"  Temp range : {min(p['temperature'] for p in packets):.1f} – {max(p['temperature'] for p in packets):.1f}")
    print(f"  Gas  range : {min(p['gas_level'] for p in packets):.1f} – {max(p['gas_level'] for p in packets):.1f}")
    return packets


# =====================================================================
#  STEP 2 — VALIDATE HAZARD CLASSIFICATION
# =====================================================================
def step2_validate_hazard_logic(packets: List[Dict]):
    print("\n" + "=" * 70)
    print("  STEP 2 — VALIDATE HAZARD CLASSIFICATION")
    print("=" * 70)

    mismatches = 0
    for i, pkt in enumerate(packets):
        temp = pkt["temperature"]
        gas = pkt["gas_level"]
        actual = classify_risk(temp, gas)

        # Expected logic per spec
        if temp > RISK_TEMP_HIGH or gas > RISK_GAS_HIGH:
            expected = "HIGH"
        elif temp > RISK_TEMP_MEDIUM or gas > RISK_GAS_MEDIUM:
            expected = "MEDIUM"
        else:
            expected = "SAFE"

        if actual != expected:
            mismatches += 1
            print(f"  MISMATCH #{i}: temp={temp} gas={gas} → expected={expected}, got={actual}")

    record("Hazard Detection", mismatches == 0,
           f"{mismatches} mismatches" if mismatches else "All 30 classifications correct")

    # ── Boundary value tests ──
    print("\n  Boundary value analysis:")
    bvt_cases = [
        (70.0, 70.0, "MEDIUM"),   # EXACTLY at threshold → NOT greater-than → MEDIUM only if >40
        (70.01, 50.0, "HIGH"),
        (50.0, 70.01, "HIGH"),
        (40.0, 40.0, "SAFE"),     # EXACTLY at medium threshold → NOT greater-than → SAFE
        (40.01, 10.0, "MEDIUM"),
        (10.0, 40.01, "MEDIUM"),
        (20.0, 10.0, "SAFE"),
        (0.0, 0.0, "SAFE"),
        (100.0, 100.0, "HIGH"),
        (-10.0, -5.0, "SAFE"),    # Negative values — should still be SAFE
    ]
    bvt_fail = 0
    for temp, gas, expected in bvt_cases:
        actual = classify_risk(temp, gas)
        status = "OK" if actual == expected else "FAIL"
        if actual != expected:
            bvt_fail += 1
            print(f"    {FAIL} BVT: temp={temp}, gas={gas} → expected={expected}, got={actual}")
        else:
            print(f"    ✓ BVT: temp={temp}, gas={gas} → {actual}")

    record("Hazard Detection — BVT", bvt_fail == 0,
           f"{bvt_fail} boundary failures" if bvt_fail else "All boundary cases correct")

    # ── Verify risk_to_cost mapping ──
    print("\n  Risk-to-cost mapping:")
    cost_ok = True
    for risk, expected_cost in [("HIGH", COST_HIGH), ("MEDIUM", COST_MEDIUM), ("SAFE", COST_SAFE)]:
        actual_cost = risk_to_cost(risk)
        if actual_cost != expected_cost:
            cost_ok = False
            print(f"    {FAIL} risk_to_cost('{risk}') = {actual_cost}, expected {expected_cost}")
        else:
            print(f"    ✓ risk_to_cost('{risk}') = {actual_cost}")
    # Unknown risk level
    unknown_cost = risk_to_cost("UNKNOWN")
    if unknown_cost != COST_SAFE:
        cost_ok = False
        print(f"    {FAIL} risk_to_cost('UNKNOWN') = {unknown_cost}, expected {COST_SAFE} (fallback)")
    else:
        print(f"    ✓ risk_to_cost('UNKNOWN') = {unknown_cost} (fallback)")

    record("Hazard Detection — Cost Mapping", cost_ok)


# =====================================================================
#  STEP 3 — VALIDATE GRID MAP
# =====================================================================
def step3_validate_grid(packets: List[Dict]):
    print("\n" + "=" * 70)
    print("  STEP 3 — VALIDATE GRID MAPPING")
    print("=" * 70)

    grid = GridMap()

    # ── Size check ──
    size_ok = grid.width == 50 and grid.height == 50
    record("Grid Mapping — Size", size_ok, f"Got {grid.width}x{grid.height}")

    # ── Bounds check ──
    print("\n  Out-of-bounds update tests:")
    oob_cases = [(-1, 0), (0, -1), (50, 0), (0, 50), (100, 100)]
    oob_ok = True
    for x, y in oob_cases:
        try:
            grid.update_cell(x, y, "HIGH")
            # Should silently ignore, check grid remains clean
            print(f"    ✓ ({x},{y}) silently ignored (no crash)")
        except Exception as e:
            oob_ok = False
            print(f"    {FAIL} ({x},{y}) raised {type(e).__name__}: {e}")
    record("Grid Mapping — OOB Safety", oob_ok)

    # ── Apply packets ──
    expected_cells: Dict[Tuple[int,int], str] = {}
    for pkt in packets:
        x, y = pkt["location"]
        risk = classify_risk(pkt["temperature"], pkt["gas_level"])
        grid.update_cell(x, y, risk, pkt["timestamp"])
        # Grid only upgrades: SAFE→MEDIUM is a max(), HIGH always overwrites
        prev = expected_cells.get((x, y), "SAFE")
        if risk == "HIGH":
            expected_cells[(x, y)] = "HIGH"
        elif risk == "MEDIUM" and prev != "HIGH":
            expected_cells[(x, y)] = "MEDIUM"
        # SAFE never downgrades — this is the ACTUAL behavior in code (line 41)

    # ── Verify cells match ──
    cell_mismatches = 0
    for (x, y), expected_risk in expected_cells.items():
        actual_risk = grid.get_risk_at(x, y)
        if actual_risk != expected_risk:
            cell_mismatches += 1
            print(f"    {FAIL} Cell ({x},{y}): expected={expected_risk}, got={actual_risk}")

    record("Grid Mapping — Cell Accuracy", cell_mismatches == 0,
           f"{cell_mismatches} mismatched cells" if cell_mismatches else
           f"All {len(expected_cells)} updated cells correct")

    # ── Weight grid ──
    wg = grid.get_weight_grid()
    wg_ok = len(wg) == 50 and all(len(row) == 50 for row in wg)
    record("Grid Mapping — Weight Grid Dims", wg_ok)

    # ── Coverage tracking ──
    visited = grid.get_visited_count()
    expected_visited = len(expected_cells)
    record("Grid Mapping — Coverage", visited == expected_visited,
           f"Visited={visited}, expected={expected_visited}")

    # ── SAFE cell never downgrades to SAFE after HIGH ──
    print("\n  Downgrade protection test:")
    grid2 = GridMap()
    grid2.update_cell(5, 5, "HIGH")
    grid2.update_cell(5, 5, "SAFE")  # Should NOT downgrade
    actual = grid2.get_risk_at(5, 5)
    downgrade_ok = actual == "HIGH"
    record("Grid Mapping — No Downgrade", downgrade_ok,
           f"After HIGH→SAFE update, cell is '{actual}' (expected HIGH)")
    if not downgrade_ok:
        BUGS.append("CRITICAL: Grid allows HIGH→SAFE downgrade — risk cells can be silently cleared")
        SUGGESTIONS.append("GridMap.update_cell should never lower a cell from HIGH→anything")

    return grid


# =====================================================================
#  STEP 4 — SURVIVOR DETECTION
# =====================================================================
def step4_test_survivor_detection():
    print("\n" + "=" * 70)
    print("  STEP 4 — SURVIVOR DETECTION (probabilistic)")
    print("=" * 70)

    # Run many trials to validate probabilities
    trials = 10000
    random.seed(99)
    counts = {"SAFE": 0, "MEDIUM": 0, "HIGH": 0}

    for risk in ["SAFE", "MEDIUM", "HIGH"]:
        for _ in range(trials):
            result = detect_survivor(25, 25, risk, timestamp=time.time())
            if result is not None:
                counts[risk] += 1

    rates = {k: v / trials for k, v in counts.items()}
    print(f"  Detection rates over {trials} trials per risk:")
    print(f"    SAFE   → {rates['SAFE']:.4f}  (config={PROB_SAFE})")
    print(f"    MEDIUM → {rates['MEDIUM']:.4f}  (config={PROB_MEDIUM})")
    print(f"    HIGH   → {rates['HIGH']:.4f}  (config={PROB_HIGH})")

    # Verify ordering: SAFE > MEDIUM > HIGH
    order_ok = rates["SAFE"] > rates["MEDIUM"] > rates["HIGH"]
    record("Survivor Detection — Probability Order", order_ok,
           "SAFE > MEDIUM > HIGH confirmed" if order_ok else
           f"Order violated: SAFE={rates['SAFE']:.4f} MEDIUM={rates['MEDIUM']:.4f} HIGH={rates['HIGH']:.4f}")

    # Verify rates are within statistical tolerance (±50% of config)
    tolerance = 0.5
    rate_accuracy = True
    for risk, expected in [("SAFE", PROB_SAFE), ("MEDIUM", PROB_MEDIUM), ("HIGH", PROB_HIGH)]:
        actual = rates[risk]
        if expected > 0:
            deviation = abs(actual - expected) / expected
            if deviation > tolerance:
                rate_accuracy = False
                print(f"    {FAIL} {risk}: observed={actual:.4f}, expected≈{expected}, deviation={deviation:.1%}")
    record("Survivor Detection — Rate Accuracy", rate_accuracy)

    # Verify survivor record structure
    print("\n  Survivor record structure validation:")
    random.seed(1)
    # Force a detection
    survivor = detect_survivor(10, 20, "SAFE", timestamp=1234567.0,
                                probabilities={"SAFE": 1.0, "MEDIUM": 1.0, "HIGH": 1.0})
    struct_ok = True
    required_fields = ["id", "x", "y", "location", "timestamp", "status", "risk_level_at_detection", "confidence"]
    if survivor is None:
        struct_ok = False
        print(f"    {FAIL} Forced detection returned None")
    else:
        for field in required_fields:
            if field not in survivor:
                struct_ok = False
                print(f"    {FAIL} Missing field: {field}")
            else:
                print(f"    ✓ {field} = {survivor[field]}")
        # Verify values
        if survivor.get("x") != 10 or survivor.get("y") != 20:
            struct_ok = False
            print(f"    {FAIL} Location mismatch: ({survivor.get('x')}, {survivor.get('y')})")
        if survivor.get("timestamp") != 1234567.0:
            struct_ok = False
            print(f"    {FAIL} Timestamp mismatch: {survivor.get('timestamp')}")
        if survivor.get("location") != (10, 20):
            struct_ok = False
            print(f"    {FAIL} Location tuple mismatch: {survivor.get('location')}")

    record("Survivor Detection — Record Structure", struct_ok)


# =====================================================================
#  STEP 5 — DUPLICATE FILTERING
# =====================================================================
def step5_test_duplicate_filter():
    print("\n" + "=" * 70)
    print("  STEP 5 — DUPLICATE FILTERING")
    print("=" * 70)

    db = VictimDB()
    base_time = time.time()

    # Add initial survivor
    original = {
        "id": "VICTIM-ORIG01", "x": 20, "y": 20,
        "location": (20, 20), "timestamp": base_time, "status": "VERIFIED"
    }
    db.add_survivor(original)

    # ── Test 1: Exact same location + close time → DUPLICATE ──
    dup1 = {"id": "VICTIM-DUP01", "x": 20, "y": 20, "timestamp": base_time + 5}
    is_dup = is_duplicate(dup1, db)
    record("Duplicate Filter — Same Location/Time", is_dup,
           "Correctly flagged as duplicate" if is_dup else "MISSED duplicate")

    # ── Test 2: Very close location + close time → DUPLICATE ──
    dup2 = {"id": "VICTIM-DUP02", "x": 21, "y": 21, "timestamp": base_time + 10}
    dist = calculate_distance((20, 20), (21, 21))
    is_dup2 = is_duplicate(dup2, db)
    within_threshold = dist <= SURVIVOR_DIST_THRESHOLD
    if within_threshold:
        record("Duplicate Filter — Near Location", is_dup2,
               f"dist={dist:.2f} ≤ threshold={SURVIVOR_DIST_THRESHOLD}" +
               (" → correctly flagged" if is_dup2 else " → MISSED"))
    else:
        record("Duplicate Filter — Near Location", not is_dup2,
               f"dist={dist:.2f} > threshold={SURVIVOR_DIST_THRESHOLD} → correctly allowed")

    # ── Test 3: Same location BUT time way apart → NOT duplicate ──
    dup3 = {"id": "VICTIM-NODP01", "x": 20, "y": 20,
            "timestamp": base_time + SURVIVOR_TIME_THRESHOLD + 100}
    is_dup3 = is_duplicate(dup3, db)
    record("Duplicate Filter — Time Apart", not is_dup3,
           "Correctly allowed (far apart in time)" if not is_dup3 else
           f"WRONGLY flagged as duplicate (time diff >{SURVIVOR_TIME_THRESHOLD}s)")

    # ── Test 4: Far location + close time → NOT duplicate ──
    dup4 = {"id": "VICTIM-NODP02", "x": 40, "y": 40, "timestamp": base_time + 5}
    is_dup4 = is_duplicate(dup4, db)
    record("Duplicate Filter — Far Location", not is_dup4,
           "Correctly allowed" if not is_dup4 else "WRONGLY flagged")

    # ── Test 5: Empty DB → never duplicate ──
    empty_db = VictimDB()
    dup5 = {"id": "VICTIM-EMPTY", "x": 10, "y": 10, "timestamp": base_time}
    is_dup5 = is_duplicate(dup5, empty_db)
    record("Duplicate Filter — Empty DB", not is_dup5)

    # ── Test 6: Missing key in new_survivor → should raise ──
    print("\n  Malformed input tests:")
    try:
        is_duplicate({"x": 10}, db)  # missing y, timestamp
        record("Duplicate Filter — Missing Key", False, "Did NOT raise on missing key")
    except (ValidationError, KeyError) as e:
        record("Duplicate Filter — Missing Key", True, f"Correctly raised: {e}")

    # ── Test 7: Malformed survivor in DB → should skip, not crash ──
    db2 = VictimDB()
    db2.add_survivor({"bad": "record"})  # no x, y, timestamp
    good = {"id": "VICTIM-G01", "x": 5, "y": 5, "timestamp": base_time}
    try:
        result = is_duplicate(good, db2)
        record("Duplicate Filter — Malformed DB Record", True,
               "Skipped malformed record without crash")
    except Exception as e:
        record("Duplicate Filter — Malformed DB Record", False,
               f"Crashed on malformed DB record: {e}")


# =====================================================================
#  STEP 6 — DATABASE VALIDATION
# =====================================================================
def step6_validate_database():
    print("\n" + "=" * 70)
    print("  STEP 6 — DATABASE VALIDATION")
    print("=" * 70)

    db = VictimDB()

    # ── Add and count ──
    base_time = time.time()
    for i in range(10):
        db.add_survivor({
            "id": f"VICTIM-DB{i:03d}",
            "x": i * 5, "y": i * 5,
            "location": (i * 5, i * 5),
            "timestamp": base_time + i,
            "status": "VERIFIED",
        })

    count = db.get_count()
    record("Database — Count", count == 10, f"Expected 10, got {count}")

    # ── No duplicates by ID ──
    all_survivors = db.get_all()
    ids = [s["id"] for s in all_survivors]
    unique_ids = len(set(ids))
    record("Database — Unique IDs", unique_ids == len(ids),
           f"{len(ids)} total, {unique_ids} unique")

    # ── Each has location + timestamp ──
    fields_ok = True
    for s in all_survivors:
        if "x" not in s or "y" not in s or "timestamp" not in s:
            fields_ok = False
            print(f"    {FAIL} Survivor {s.get('id', '?')} missing required fields")
    record("Database — Required Fields", fields_ok)

    # ── get_by_id ──
    found = db.get_by_id("VICTIM-DB005")
    record("Database — get_by_id", found is not None and found["x"] == 25)

    # ── get_latest ──
    latest = db.get_latest()
    record("Database — get_latest", latest is not None and latest["id"] == "VICTIM-DB009",
           f"Latest={latest['id']}" if latest else "None")

    # ── remove ──
    removed = db.remove("VICTIM-DB005")
    new_count = db.get_count()
    record("Database — Remove", removed and new_count == 9)

    # ── reset ──
    db.reset()
    record("Database — Reset", db.get_count() == 0)

    # ── Thread safety stress test ──
    print("\n  Thread safety stress test (100 concurrent writes):")
    db2 = VictimDB()
    errors = []

    def add_many(start: int):
        for i in range(25):
            try:
                db2.add_survivor({"id": f"T-{start}-{i}", "x": i, "y": i, "timestamp": time.time()})
            except Exception as e:
                errors.append(str(e))

    threads = [threading.Thread(target=add_many, args=(t,)) for t in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    record("Database — Thread Safety", len(errors) == 0 and db2.get_count() == 100,
           f"Stored {db2.get_count()}/100, errors={len(errors)}")


# =====================================================================
#  STEP 7 — PATHFINDING TEST
# =====================================================================
def step7_pathfinding(grid: GridMap):
    print("\n" + "=" * 70)
    print("  STEP 7 — PATHFINDING (A*)")
    print("=" * 70)

    weight_grid = grid.get_weight_grid()

    # ── Test 1: Basic path (0,0) → (49,49) ──
    path = a_star(weight_grid, (0, 0), (49, 49))
    if path is None:
        record("Pathfinding — Basic Path", False, "No path found (0,0)→(49,49)")
    else:
        record("Pathfinding — Basic Path", len(path) > 0,
               f"Path found with {len(path)} steps")

        # Verify path avoids HIGH-risk cells
        high_violations = []
        for (px, py) in path:
            if weight_grid[py][px] >= COST_HIGH:
                high_violations.append((px, py))

        record("Pathfinding — Avoids HIGH", len(high_violations) == 0,
               f"{len(high_violations)} HIGH cells on path" if high_violations else
               "Path never crosses HIGH-risk cells")

        # Verify path is contiguous (each step ≤ sqrt(2) apart)
        contiguous = True
        for i in range(1, len(path)):
            dx = abs(path[i][0] - path[i-1][0])
            dy = abs(path[i][1] - path[i-1][1])
            if dx > 1 or dy > 1:
                contiguous = False
                print(f"    {FAIL} Discontinuity at step {i}: {path[i-1]} → {path[i]}")
        record("Pathfinding — Contiguity", contiguous)

        # Verify start and end
        record("Pathfinding — Start/End", path[0] == (0, 0) and path[-1] == (49, 49),
               f"Start={path[0]}, End={path[-1]}")

        # Path length reasonableness (Manhattan ≤ path ≤ 3*Manhattan for diagonal)
        manhattan = abs(49 - 0) + abs(49 - 0)  # = 98
        min_diag = math.ceil(max(49, 49))  # ~49 for 8-dir
        reasonable = min_diag <= len(path) <= manhattan * 3
        record("Pathfinding — Length Reasonable", reasonable,
               f"Length={len(path)}, min_diag={min_diag}, manhattan={manhattan}")

    # ── Test 2: Same start & end ──
    same_path = a_star(weight_grid, (5, 5), (5, 5))
    record("Pathfinding — Same Start/End", same_path is not None and len(same_path) == 1)

    # ── Test 3: Out of bounds ──
    oob_path = a_star(weight_grid, (-1, -1), (49, 49))
    record("Pathfinding — OOB Start", oob_path is None)

    oob_path2 = a_star(weight_grid, (0, 0), (50, 50))
    record("Pathfinding — OOB Goal", oob_path2 is None)

    # ── Test 4: Clean grid ── fastest possible ──
    clean_grid = [[COST_SAFE] * 50 for _ in range(50)]
    clean_path = a_star(clean_grid, (0, 0), (49, 49))
    record("Pathfinding — Clean Grid", clean_path is not None and len(clean_path) > 0,
           f"Length={len(clean_path) if clean_path else 'None'}")

    # ── Test 5: Heuristic admissibility check ──
    h = heuristic((0, 0), (49, 49))
    actual_dist = math.sqrt(49**2 + 49**2)
    record("Pathfinding — Heuristic", abs(h - actual_dist) < 0.001,
           f"heuristic={h:.4f}, actual_euclidean={actual_dist:.4f}")


# =====================================================================
#  STEP 8 — API VALIDATION (unit-level, no Flask server needed)
# =====================================================================
def step8_api_validation():
    print("\n" + "=" * 70)
    print("  STEP 8 — API VALIDATION (server module integration)")
    print("=" * 70)

    # Import the server's backend directly (no HTTP needed)
    from server import AuraBackend, _serialize_path

    be = AuraBackend()

    # ── Send 10 packets through the pipeline ──
    random.seed(77)
    for i in range(10):
        pkt = {
            "drone_id": random.randint(1, 4),
            "temperature": round(random.uniform(20, 100), 2),
            "gas_level": round(random.uniform(10, 100), 2),
            "location": [random.randint(0, 49), random.randint(0, 49)],
            "timestamp": time.time() + i,
        }
        result = be.process_sensor_packet(pkt)
        assert "risk" in result, f"Missing 'risk' in pipeline result"
        assert "survivor_detected" in result
        assert "duplicate" in result
        assert "path" in result or result.get("path") is None

    # ── GET /grid equivalent ──
    state = be.get_state()
    grid_data = state["grid"]
    grid_ok = (isinstance(grid_data, list) and
               len(grid_data) == 50 and
               all(len(r) == 50 for r in grid_data))
    record("API — /grid", grid_ok, f"Grid is {len(grid_data)}x{len(grid_data[0]) if grid_data else '?'}")

    # ── GET /survivors equivalent ──
    survivors = state["survivors"]
    record("API — /survivors", isinstance(survivors, list),
           f"Returns list with {len(survivors)} entries")

    # Each survivor must have x, y, timestamp
    api_fields_ok = all("x" in s and "y" in s and "timestamp" in s for s in survivors)
    record("API — /survivors fields", api_fields_ok or len(survivors) == 0)

    # ── GET /path equivalent ──
    path = be.compute_path((25, 25), (0, 0))
    serialized = _serialize_path(path)
    if path is not None:
        record("API — /path", serialized is not None and len(serialized) > 0,
               f"Path with {len(serialized)} steps")
        # Verify serialized format is list of (int, int) tuples
        fmt_ok = all(isinstance(p, (list, tuple)) and len(p) == 2 for p in serialized)
        record("API — /path format", fmt_ok)
    else:
        record("API — /path", True, "No path available (target may be High risk)")

    # ── _serialize_path(None) should return None, not crash ──
    record("API — serialize None", _serialize_path(None) is None)

    # ── Consistency: grid + survivors + path from same state ──
    # Re-check state after pipeline
    state2 = be.get_state()
    consistency_ok = (
        "grid" in state2 and
        "survivors" in state2 and
        "last_path" in state2 and
        "last_goal" in state2
    )
    record("API — State Consistency", consistency_ok)

    # ── Input validation via normalize_sensor_payload ──
    print("\n  Input validation tests:")
    bad_payloads = [
        ({}, "empty payload"),
        ({"drone_id": 1}, "missing fields"),
        ({"drone_id": "abc", "temperature": 30, "gas_level": 20,
          "location": [10, 10], "timestamp": 0}, "string drone_id — should coerce"),
        ({"drone_id": 1, "temperature": 30, "gas_level": 20,
          "location": [60, 10], "timestamp": 0}, "OOB location"),
        ({"drone_id": 1, "temperature": 30, "gas_level": 20,
          "location": "not_a_list", "timestamp": 0}, "bad location type"),
    ]
    for payload, desc in bad_payloads:
        try:
            normalized = normalize_sensor_payload(payload)
            if desc == "string drone_id — should coerce":
                record(f"API — Input: {desc}", True, "Coerced successfully")
            elif desc == "OOB location":
                record(f"API — Input: {desc}", False, "Should have raised ValidationError")
            else:
                record(f"API — Input: {desc}", False, "Should have raised ValidationError")
        except ValidationError as ve:
            if desc == "string drone_id — should coerce":
                record(f"API — Input: {desc}", False, f"Unexpected rejection: {ve}")
            else:
                record(f"API — Input: {desc}", True, f"Correctly rejected: {ve}")
        except Exception as e:
            record(f"API — Input: {desc}", False, f"Wrong exception type: {type(e).__name__}: {e}")


# =====================================================================
#  STEP 9 — EDGE CASES
# =====================================================================
def step9_edge_cases():
    print("\n" + "=" * 70)
    print("  STEP 9 — EDGE CASES (trying to break the system)")
    print("=" * 70)

    # ── 9.1: All HIGH grid → path should fail ──
    print("\n  9.1 — ALL HIGH grid")
    all_high = [[COST_HIGH] * 50 for _ in range(50)]
    path_high = a_star(all_high, (0, 0), (49, 49))
    record("Edge — All HIGH Grid", path_high is None,
           "Correctly returns None (no safe path)" if path_high is None else
           f"WRONGLY returned path of length {len(path_high)}")

    # ── 9.2: Corridor — only one safe path ──
    print("\n  9.2 — Single corridor")
    corridor = [[COST_HIGH] * 50 for _ in range(50)]
    for x in range(50):
        corridor[0][x] = COST_SAFE   # Top row safe
        corridor[49][x] = COST_SAFE  # Bottom row safe
    corridor[0][49] = COST_SAFE  # connect corner
    for y in range(50):
        corridor[y][49] = COST_SAFE  # Right column safe
    path_corr = a_star(corridor, (0, 0), (49, 49))
    if path_corr:
        # Verify all cells on path are SAFE
        safe_violations = [(px, py) for px, py in path_corr if corridor[py][px] >= COST_HIGH]
        record("Edge — Corridor Path", len(safe_violations) == 0,
               f"Path found ({len(path_corr)} steps), {len(safe_violations)} violations")
    else:
        record("Edge — Corridor Path", False, "No path found through corridor")

    # ── 9.3: No survivors → empty list ──
    print("\n  9.3 — No survivors DB")
    db = VictimDB()
    record("Edge — Empty Survivors", db.get_all() == [] and db.get_count() == 0)
    record("Edge — get_latest None", db.get_latest() is None)

    # ── 9.4: Repeated exact same data → no duplicate survivors ──
    print("\n  9.4 — Repeated identical data (30x)")
    db2 = VictimDB()
    base_time = time.time()
    added = 0
    for _ in range(30):
        survivor = {
            "id": f"VICTIM-REP{_:03d}", "x": 15, "y": 15,
            "location": (15, 15), "timestamp": base_time, "status": "VERIFIED",
        }
        if not is_duplicate(survivor, db2):
            db2.add_survivor(survivor)
            added += 1

    # First should be added, remaining 29 should be duplicates
    record("Edge — Repeated Data", added == 1,
           f"Added {added}/30 (expected 1)")

    # ── 9.5: SensorSimulator with extreme hotspot ──
    print("\n  9.5 — Extreme hotspot proximity")
    sim = SensorSimulator()
    sim.hotspots = [{"x": 25, "y": 25, "intensity": 200}]  # extreme

    class FakeDrone:
        drone_id = 99
        x = 25
        y = 25

    reading = sim.read_sensor_data(FakeDrone())
    extreme_risk = classify_risk(reading["temp"], reading["gas"])
    record("Edge — Extreme Hotspot", extreme_risk == "HIGH",
           f"temp={reading['temp']}, gas={reading['gas']}, risk={extreme_risk}")

    # ── 9.6: generate_sensor_data always in bounds ──
    print("\n  9.6 — 1000x generated data bounds check")
    random.seed(123)
    oob_count = 0
    for _ in range(1000):
        d = generate_sensor_data(drone_id=1)
        loc = d["location"]
        if loc[0] < 0 or loc[0] > 49 or loc[1] < 0 or loc[1] > 49:
            oob_count += 1
    record("Edge — Generator Bounds", oob_count == 0,
           f"{oob_count} out-of-bounds in 1000 samples")

    # ── 9.7: GridMap update_cell with SAFE does NOT change HIGH cell ──
    print("\n  9.7 — Risk level monotonicity")
    grid = GridMap()
    grid.update_cell(10, 10, "HIGH")
    grid.update_cell(10, 10, "MEDIUM")  # Should NOT downgrade
    grid.update_cell(10, 10, "SAFE")    # Should NOT downgrade
    final_risk = grid.get_risk_at(10, 10)
    record("Edge — Risk Monotonicity", final_risk == "HIGH",
           f"After HIGH→MEDIUM→SAFE, cell is '{final_risk}'")
    if final_risk != "HIGH":
        BUGS.append(f"CRITICAL: Cell risk downgraded from HIGH to {final_risk}")

    # ── 9.8: MEDIUM→SAFE should also not downgrade ──
    grid2 = GridMap()
    grid2.update_cell(10, 10, "MEDIUM")
    grid2.update_cell(10, 10, "SAFE")
    final2 = grid2.get_risk_at(10, 10)
    record("Edge — MEDIUM→SAFE Monotonicity", final2 == "MEDIUM",
           f"After MEDIUM→SAFE, cell is '{final2}'")

    # ── 9.9: A* with start on HIGH cell ──
    print("\n  9.9 — Start/Goal on HIGH cell")
    blocked_grid = [[COST_SAFE] * 50 for _ in range(50)]
    blocked_grid[0][0] = COST_HIGH  # Start is HIGH
    path_blocked_start = a_star(blocked_grid, (0, 0), (49, 49))
    # A* should skip HIGH cells — if start is HIGH, path may still be None
    # Actually, looking at the code, it only skips neighbors >= COST_HIGH,
    # but the start cell is never checked. Let's see what happens.
    if path_blocked_start is not None:
        # If path exists, it starts from a HIGH cell — this is a potential bug
        print(f"    Path found starting from HIGH cell ({len(path_blocked_start)} steps)")
        record("Edge — HIGH Start", False,
               "Path starts from HIGH cell — A* should reject HIGH start")
        BUGS.append("A* allows pathfinding FROM a HIGH-risk cell (start not validated)")
        SUGGESTIONS.append("Add start-cell validation in a_star(): reject if start is HIGH")
    else:
        record("Edge — HIGH Start", True, "Correctly rejected HIGH start")

    # Goal on HIGH cell
    blocked_grid2 = [[COST_SAFE] * 50 for _ in range(50)]
    blocked_grid2[49][49] = COST_HIGH
    path_blocked_goal = a_star(blocked_grid2, (0, 0), (49, 49))
    # A* skips neighbors >= COST_HIGH, so goal should be unreachable
    record("Edge — HIGH Goal", path_blocked_goal is None,
           "Correctly rejected HIGH goal" if path_blocked_goal is None else
           f"WRONGLY found path to HIGH cell ({len(path_blocked_goal)} steps)")

    # ── 9.10: Large-scale duplicate storm ──
    print("\n  9.10 — Duplicate storm (500 detections in burst)")
    db3 = VictimDB()
    storm_base = time.time()
    storm_added = 0
    for i in range(500):
        s = {
            "id": f"STORM-{i:04d}",
            "x": random.randint(0, 5),    # Tight cluster
            "y": random.randint(0, 5),
            "timestamp": storm_base + random.uniform(0, 10),  # Within time threshold
        }
        if not is_duplicate(s, db3, distance_threshold=3.0, time_threshold=60.0):
            db3.add_survivor(s)
            storm_added += 1
    record("Edge — Duplicate Storm", storm_added < 500,
           f"Added {storm_added}/500 in tight cluster (dedup working)")


# =====================================================================
#  FINAL REPORT
# =====================================================================
def print_report():
    print("\n\n")
    print("=" * 70)
    print("  📊 AURA E2E TEST REPORT")
    print("=" * 70)

    # ── Module rollup ──
    modules = {
        "Hazard Detection": [],
        "Grid Mapping": [],
        "Survivor Detection": [],
        "Duplicate Filtering": [],
        "Database": [],
        "Pathfinding": [],
        "API": [],
        "Edge Cases": [],
    }

    for test_name, status in results.items():
        matched = False
        for module_prefix in modules:
            short = module_prefix.split(" — ")[0]
            if test_name.startswith(short) or test_name.startswith(module_prefix):
                modules[module_prefix].append((test_name, status))
                matched = True
                break
        if not matched:
            if "Edge" in test_name:
                modules["Edge Cases"].append((test_name, status))
            elif "API" in test_name:
                modules["API"].append((test_name, status))

    print("\n  MODULE RESULTS:")
    print("  " + "-" * 50)
    total_pass = 0
    total_fail = 0
    for module, tests in modules.items():
        if not tests:
            continue
        passes = sum(1 for _, s in tests if s == "PASS")
        fails = sum(1 for _, s in tests if s == "FAIL")
        total_pass += passes
        total_fail += fails
        icon = "✅" if fails == 0 else "❌"
        status = "PASS" if fails == 0 else "FAIL"
        print(f"  {icon} {module:30s} {status:6s}  ({passes}/{len(tests)} tests)")

    print("  " + "-" * 50)
    total = total_pass + total_fail
    print(f"  TOTAL: {total_pass}/{total} passed, {total_fail} failed\n")

    # ── Bugs ──
    if BUGS:
        print("  🐛 BUGS FOUND:")
        print("  " + "-" * 50)
        for i, bug in enumerate(BUGS, 1):
            print(f"  {i}. {bug}")
    else:
        print("  🐛 No bugs found — all modules functioning correctly!")

    # ── Suggestions ──
    print()
    # Always include hardened suggestions
    all_suggestions = list(SUGGESTIONS)
    all_suggestions.extend([
        "Add input sanitization for negative temp/gas values in classify_risk",
        "Consider adding a max-iterations guard to A* to prevent pathological runtime on huge grids",
        "VictimDB should enforce unique IDs on insert (currently allows duplicates if is_duplicate not called)",
        "Add persistent storage (SQLite) for victim_db to survive server restarts",
        "Add rate-limiting to /data endpoint to prevent sensor data flooding",
        "Consider time-decaying risk: cells should gradually return to SAFE if no new HIGH readings",
        "Add logging/alerting when duplicate detection rejects a survivor for audit trail",
    ])

    print("  💡 SUGGESTIONS:")
    print("  " + "-" * 50)
    for i, s in enumerate(all_suggestions, 1):
        print(f"  {i}. {s}")

    print("\n" + "=" * 70)
    overall = "✅ SYSTEM PASS" if total_fail == 0 else f"❌ SYSTEM FAIL ({total_fail} failures)"
    print(f"  OVERALL: {overall}")
    print("=" * 70)


# =====================================================================
#  MAIN
# =====================================================================
if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("  AURA — FULL END-TO-END SYSTEM TEST")
    print("  Pipeline: sensor → hazard → grid → survivor → dedup → DB → path → API")
    print("█" * 70)

    packets = step1_simulate_data_stream()
    step2_validate_hazard_logic(packets)
    grid = step3_validate_grid(packets)
    step4_test_survivor_detection()
    step5_test_duplicate_filter()
    step6_validate_database()
    step7_pathfinding(grid)
    step8_api_validation()
    step9_edge_cases()
    print_report()
