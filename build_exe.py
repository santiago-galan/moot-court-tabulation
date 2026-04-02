"""Build a standalone MCTS distribution using PyInstaller."""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist", "MCTS")


def main():
    print("Building MCTS standalone distribution...")

    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--name", "MCTS",
        "--console",
        "--noconfirm",
        "--clean",
        "--add-data", f"server{os.pathsep}server",
        "--add-data", f"client/dist{os.pathsep}client/dist",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "server.main",
        "--hidden-import", "server.api.rulesets",
        "--hidden-import", "server.api.tournaments",
        "--hidden-import", "server.api.teams",
        "--hidden-import", "server.api.rounds",
        "--hidden-import", "server.api.scoring",
        "--hidden-import", "server.api.brackets",
        "--hidden-import", "server.api.reports",
        "--hidden-import", "server.api.judge_portal",
        "--hidden-import", "server.api.network",
        "launcher.py",
    ], cwd=ROOT)

    print(f"\nDone! Distribution at: {DIST}")
    print(f"Run: {os.path.join(DIST, 'MCTS.exe')}")


if __name__ == "__main__":
    main()
