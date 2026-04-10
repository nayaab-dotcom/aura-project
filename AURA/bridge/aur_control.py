"""
aur_control.py

Bidirectional bridge from Flask backend to ESP32 over serial (USB / HC-12).
Provides send_command(data: dict) which JSON-encodes and transmits with
newline termination. Includes reconnect logic and simple logging.
"""

import json
import os
import threading
import time
from typing import Optional

import serial
from serial.serialutil import SerialException

SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")
BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))
WRITE_TIMEOUT = float(os.getenv("WRITE_TIMEOUT", "1.0"))
RECONNECT_DELAY = float(os.getenv("RECONNECT_DELAY", "3.0"))
# Allow running without hardware for local dev / CI (default: disabled)
DISABLE_SERIAL = os.getenv("DISABLE_SERIAL", "1") == "1"


class SerialCommandBridge:
    def __init__(self):
        self.ser: Optional[serial.Serial] = None
        self.lock = threading.Lock()
        if DISABLE_SERIAL:
            self._log("WARN", "Serial disabled (DISABLE_SERIAL=1); commands will be skipped")
        else:
            self._connect()

    def _connect(self):
        """Establish serial connection with retries."""
        if DISABLE_SERIAL:
            return
        while True:
            try:
                self.ser = serial.Serial(
                    SERIAL_PORT,
                    BAUD_RATE,
                    timeout=WRITE_TIMEOUT,
                    write_timeout=WRITE_TIMEOUT,
                )
                self._log("INFO", f"Connected to {SERIAL_PORT} @ {BAUD_RATE}")
                return
            except SerialException as exc:
                self._log("ERROR", f"Serial open failed: {exc}; retrying in {RECONNECT_DELAY}s")
                time.sleep(RECONNECT_DELAY)

    def _ensure_connected(self):
        """Reconnect if the port has closed."""
        if DISABLE_SERIAL:
            return
        if self.ser is None or not self.ser.is_open:
            self._log("WARN", "Serial disconnected; reconnecting")
            self._connect()

    def send_command(self, data: dict) -> bool:
        """
        Encode a dict as JSON and send over serial with newline.
        Returns True on success, False on failure.
        """
        if DISABLE_SERIAL:
            self._log("INFO", f"Serial disabled. Dropping command: {data}")
            return True
        payload = json.dumps(data, separators=(",", ":"))
        message = payload + "\n"

        with self.lock:
            self._ensure_connected()
            try:
                self.ser.write(message.encode("utf-8"))
                self.ser.flush()
                self._log("SENT", payload)
                return True
            except SerialException as exc:
                self._log("ERROR", f"Write failed: {exc}; attempting reconnect")
                try:
                    self.ser.close()
                except Exception:
                    pass
                self._connect()
                return False
            except Exception as exc:  # catch unexpected errors to keep service alive
                self._log("ERROR", f"Unexpected send error: {exc}")
                return False

    @staticmethod
    def _log(prefix: str, message: str):
        print(f"[{prefix}] {message}", flush=True)


# Singleton bridge for importers
bridge = SerialCommandBridge()

def send_command(data: dict) -> bool:
    """Module-level helper to keep existing imports simple."""
    return bridge.send_command(data)
