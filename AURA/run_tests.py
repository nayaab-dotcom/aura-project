"""Runner script that captures test output to a UTF-8 file."""
import sys, io, os

# Redirect stdout to file
output_path = os.path.join(os.path.dirname(__file__), "test_output.txt")
original_stdout = sys.stdout

class TeeWriter:
    def __init__(self, file_path):
        self.file = open(file_path, "w", encoding="utf-8")
        self.stdout = original_stdout
    def write(self, text):
        self.file.write(text)
        try:
            self.stdout.write(text)
        except:
            pass
    def flush(self):
        self.file.flush()
        self.stdout.flush()

sys.stdout = TeeWriter(output_path)

# Now run the actual test
exec(open(os.path.join(os.path.dirname(__file__), "test_e2e_full.py"), encoding="utf-8").read())

sys.stdout.file.close()
sys.stdout = original_stdout
print(f"\nResults saved to {output_path}")
