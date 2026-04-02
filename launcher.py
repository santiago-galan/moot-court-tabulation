"""
MCTS Launcher -- starts the backend server and opens the admin panel in the default browser.
Shuts everything down cleanly when the console window is closed.
"""
import atexit
import os
import signal
import subprocess
import sys
import threading
import time
import webbrowser

PORT = 8000
HOST = "0.0.0.0"


def find_project_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def main():
    root = find_project_root()
    os.chdir(root)

    print("=" * 50)
    print("  Moot Court Tabulation System")
    print("=" * 50)
    print()
    print(f"Starting server on port {PORT}...")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app", "--host", HOST, "--port", str(PORT)],
        cwd=root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )

    def cleanup():
        print("\nShutting down server...")
        try:
            if sys.platform == "win32":
                server_proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                server_proc.terminate()
            server_proc.wait(timeout=5)
        except Exception:
            server_proc.kill()
        print("Server stopped.")

    atexit.register(cleanup)

    ready = False
    for line in iter(server_proc.stdout.readline, b""):
        text = line.decode("utf-8", errors="replace").rstrip()
        print(text)
        if "Application startup complete" in text:
            ready = True
            break
        if server_proc.poll() is not None:
            print("ERROR: Server failed to start.")
            sys.exit(1)

    if not ready:
        print("ERROR: Server did not report startup.")
        sys.exit(1)

    url = f"http://localhost:{PORT}"
    print()
    print(f"Server is running at {url}")
    print("Opening admin panel in your browser...")
    print()
    print("Close this window to stop the server.")
    print()

    webbrowser.open(url)

    def stream_output():
        for line in iter(server_proc.stdout.readline, b""):
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                print(text)

    output_thread = threading.Thread(target=stream_output, daemon=True)
    output_thread.start()

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
