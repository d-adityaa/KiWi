import sys
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run",
                    str(ROOT / "dashboard" / "app.py"), "--server.port", "8501"],
                   cwd=str(ROOT))
