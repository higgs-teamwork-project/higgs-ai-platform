import subprocess
import sys
import time

def main():
    print("========================================")
    print("  Starting HIGGS AI Platform...         ")
    print("========================================")

    # 1. Start the FastAPI backend
    print("[1/2] Booting up the FastAPI backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main_api:app", "--reload"]
    )

    # Give the server 2 seconds to fully start up before launching the UI
    time.sleep(2) 

    # 2. Start the PySide6 frontend
    print("[2/2] Launching the PySide6 frontend UI...")
    frontend_process = subprocess.Popen(
        [sys.executable, "frontend/main_ui.py"]
    )

    try:
        # Wait until the user clicks the "X" to close the PySide6 window
        frontend_process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        # When the UI window closes, automatically kill the backend server so it doesn't run forever
        print("\nUI Closed. Shutting down the backend server...")
        backend_process.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()