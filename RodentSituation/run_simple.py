#!/usr/bin/env python3
"""
Simple launcher for the rodent dashboard using system Python
Ignores Homebrew completely
"""

import subprocess
import sys
import os

def main():
    """Launch the dashboard using system Python"""
    print("🚀 Starting Rodent Dashboard (System Python)")
    print("📱 Will open at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    # Use system Python to run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "rodent_dashboard.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try running: python3 -m streamlit run rodent_dashboard.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 