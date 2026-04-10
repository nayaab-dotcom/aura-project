import os
import sys
import time
import serial
from serial.serialutil import SerialException

PORT = os.getenv("SERIAL_PORT", "COM5")
BAUD = int(os.getenv("BAUD_RATE", "9600"))
TIMEOUT = float(os.getenv("SERIAL_TIMEOUT", "1.0"))

def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
        print(f"[INFO] Opened {PORT} @ {BAUD}")
    except SerialException as exc:
        print(f"[ERROR] Failed to open {PORT}: {exc}")
        sys.exit(1)

    try:
        while True:
            line = ser.readline()
            if not line:
                continue
            try:
                data = line.decode(errors="replace").strip()
            except Exception:
                data = str(line)
            print("RAW:", data)
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
