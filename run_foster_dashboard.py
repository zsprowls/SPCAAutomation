#!/usr/bin/env python3
"""
Simple script to run the foster dashboard from the main directory
"""

import os
import subprocess
import sys

def main():
    # Check if we're in the right directory
    if not os.path.exists("FosterDash"):
        print("❌ Error: FosterDash folder not found!")
        print("Please run this script from the SPCAAutomation directory.")
        return
    
    # Change to FosterDash directory and run the dashboard
    os.chdir("FosterDash")
    
    print("🚀 Starting SPCA Foster Dashboard...")
    print("📁 Running from FosterDash directory")
    print("🌐 Dashboard will be available at: http://localhost:8501")
    print("")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "foster_dashboard.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

if __name__ == "__main__":
    main() 