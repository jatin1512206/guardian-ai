import subprocess
import sys
import os

def run_setup():
    print("Configuring Python dependencies & virtual packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
    print("Backend ready. Starting client build tests...")
    
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    if os.path.exists(frontend_dir):
        subprocess.check_call("npm install", shell=True, cwd=frontend_dir)
        print("Frontend Node dependencies initialized successfully.")

if __name__ == "__main__":
    run_setup()
