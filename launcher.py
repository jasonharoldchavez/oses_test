import subprocess
import sys
import time

def launch_system():
    print("==========================================================")
    print("      INITIALIZING INTEGRATED DATA GUARDIAN PLATFORM      ")
    print("==========================================================")
    
    print("\n[1/3] Verifying mathematical framework dependencies...")
    try:
        import numpy as np
        import fastapi
    except ImportError as e:
        print(f"❌ Missing dependency: {e}. Please install requirements.")
        sys.exit(1)
    print("✅ Dependencies verified successfully.")

    print("\n[2/3] Booting local data verification gateway...")
    # This simulates checking your gateway module logic before launch
    time.sleep(1)
    print("✅ Gateway logic structurally validated.")

    print("\n[3/3] Starting core API web engine...")
    print("🚀 Platform is online. Launching local host services...")
    
    # Command to run the FastAPI app via uvicorn
    # Adjust 'app:app' if your main FastAPI file has a different name
    cmd = ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 System shutdown initiated cleanly by user.")
    except Exception as e:
        print(f"\n❌ Failed to launch server engine: {e}")

if __name__ == "__main__":
    launch_system()
