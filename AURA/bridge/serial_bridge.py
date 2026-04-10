import os
import sys
import time
import json
import traceback

import requests
import serial
from serial.serialutil import SerialException

# ---------------------------------------------------------------------------
# Configuration (override via environment variables)
# ---------------------------------------------------------------------------
SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")
BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/data")
DRONE_ID = int(os.getenv("DRONE_ID", "1"))
READ_TIMEOUT = float(os.getenv("READ_TIMEOUT", "1.0"))
RECONNECT_DELAY = float(os.getenv("RECONNECT_DELAY", "3.0"))
FAKE_LINE = os.getenv("FAKE_LINE")  # optional testing override


def log(prefix: str, message: str) -> None:
    print(f"[{prefix}] {message}", flush=True)


def connect_serial() -> serial.Serial:
    """Attempt to open the serial port, retrying on failure."""
    if FAKE_LINE:
        # No serial needed in fake-line mode
        return None
    while True:
        try:
            ser = serial.Serial(
                SERIAL_PORT,
                BAUD_RATE,
                timeout=READ_TIMEOUT,
                write_timeout=READ_TIMEOUT,
            )
            log("INFO", f"Connected to serial {SERIAL_PORT} @ {BAUD_RATE}")
            return ser
        except SerialException as exc:
            log("ERROR", f"Serial connect failed: {exc}. Retrying in {RECONNECT_DELAY}s")
            time.sleep(RECONNECT_DELAY)


def parse_line(line: str):
    """Parse a raw CSV line into structured fields."""
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 4:
        raise ValueError("Expected 4 comma-separated values")

    try:
        temp = float(parts[0])
        gas = float(parts[1])
        x = int(float(parts[2]))
        y = int(float(parts[3]))
    except ValueError as exc:
        raise ValueError(f"Non-numeric value: {exc}")

    return {
        "drone_id": DRONE_ID,
        "temperature": temp,
        "gas_level": gas,
        "location": [x, y],
    }


def send_payload(payload: dict) -> None:
    response = requests.post(API_URL, json=payload, timeout=3)
    log("SENT", f"Status: {response.status_code}")


def main():
    ser = connect_serial()

    while True:
        try:
            if FAKE_LINE:
                line = FAKE_LINE.strip()
                time.sleep(1)  # avoid tight loop
            else:
                line_bytes = ser.readline()
                if not line_bytes:
                    continue

                try:
                    line = line_bytes.decode(errors="ignore").strip()
                except Exception:
                    log("ERROR", "Failed to decode incoming bytes")
                    continue

            if not line:
                continue

            log("DATA", f"Raw: {line}")

            try:
                payload = parse_line(line)
            except Exception as exc:
                log("ERROR", f"Parse failed: {exc}")
                continue

            log("PARSED", json.dumps(payload))

            try:
                send_payload(payload)
            except Exception as exc:
                log("ERROR", f"API send failed: {exc}")
                continue

        except SerialException as exc:
            log("ERROR", f"Serial error: {exc}. Reconnecting...")
            try:
                ser.close()
            except Exception:
                pass
            time.sleep(RECONNECT_DELAY)
            ser = connect_serial()
        except KeyboardInterrupt:
            log("INFO", "Interrupted by user. Exiting.")
            try:
                ser.close()
            except Exception:
                pass
            sys.exit(0)
        except Exception as exc:
            log("ERROR", f"Unexpected error: {exc}")
            traceback.print_exc()
            # keep running


if __name__ == "__main__":
    main()
