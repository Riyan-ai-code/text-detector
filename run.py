import os
import sys
import subprocess
import threading
import time
import uvicorn

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REACT_FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def run_backend():
    print("=" * 70)
    print("[TruthLens AI] Starting Multi-Modal Authenticity & Forensics Platform")
    print("[TruthLens AI] API Gateway:      http://127.0.0.1:8000")
    print("[TruthLens AI] Swagger Docs:     http://127.0.0.1:8000/docs")
    print("[TruthLens AI] System 1: Text | System 2: Plagiarism | System 3: Docs | System 4: Voice")
    print("=" * 70)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

def run_react_frontend():
    if not os.path.exists(REACT_FRONTEND_DIR):
        print(f"[Frontend Warning] React frontend directory not found at: {REACT_FRONTEND_DIR}")
        return

    print("=" * 65)
    print("[Frontend] Starting React + Recharts Vite Dashboard...")
    print(f"[Frontend] Local URL:   http://localhost:5173")
    print("=" * 65)
    
    try:
        cmd = "npm.cmd run dev" if os.name == "nt" else "npm run dev"
        subprocess.run(cmd, shell=True, cwd=REACT_FRONTEND_DIR)
    except Exception as e:
        print(f"[Frontend Error] Could not start Vite dev server: {e}")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if "--all" in args or "--frontend" in args:
        print("Starting both Backend and React Dashboard concurrently...")
        t_frontend = threading.Thread(target=run_react_frontend, daemon=True)
        t_frontend.start()
        time.sleep(1)
        run_backend()
    else:
        run_backend()
