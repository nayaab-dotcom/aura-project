import time

def generate_mission_report(mission, grid_map, victim_db):
    """
    Computes real-time mission metrics from backend state.
    """
    duration = time.time() - mission.start_time
    survivors = victim_db.get_all()
    
    total_cells = grid_map.width * grid_map.height
    visited_cells = grid_map.get_visited_count()
    coverage = (visited_cells / total_cells) * 100 if total_cells > 0 else 0
    
    high_risk_cells = grid_map.get_high_risk_count()
    
    return {
        'mission_id': mission.id,
        'status': mission.status,
        'duration_seconds': round(duration, 1),
        'metrics': {
            'survivors_found': len(survivors),
            'coverage_percent': round(coverage, 2),
            'high_risk_detected': high_risk_cells,
            'total_cells': total_cells
        },
        'timestamp': time.time()
    }
