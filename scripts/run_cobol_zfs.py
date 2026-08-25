import subprocess as sp
from pathlib import Path

CURRENT_DIR = Path(__file__).parent
ROOT_DIR = CURRENT_DIR.parent
LOADLIB = ROOT_DIR / "loadlib"


def run(pgm_name: str):
    pgm_path = LOADLIB / pgm_name
    result = sp.run([pgm_path], capture_output=True, text=True)  # noqa: PLW1510
    print(result.stdout)


if __name__ == "__main__":
    run("vote")
