#!/usr/bin/env python
"""
Startup script for Hugging Face Spaces deployment.
This ensures FastAPI runs on port 7860 (for validators) and Streamlit on 8501 (for UI).
"""
from __future__ import annotations

import os
import sys

def main():
    # Ensure all required environment variables are set
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_CORS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION", "false")
    os.environ.setdefault("STREAMLIT_SERVER_PORT", "8501")
    os.environ.setdefault("STREAMLIT_SERVER_ADDRESS", "127.0.0.1")
    
    # HF Spaces configuration - FastAPI MUST be on port 7860
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "7860")
    
    print("[STARTUP] Starting HF Spaces with FastAPI (7860) + Streamlit (8501)...")
    
    # Import and run the combined server
    from server.run_all import main as run_server
    run_server()

if __name__ == "__main__":
    main()
