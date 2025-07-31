#!/usr/bin/env python3
"""
Simple launcher for the morning email script using system Python
Ignores Homebrew completely
"""

import subprocess
import sys
import os

def main():
    """Launch the morning email script using system Python"""
    print("📧 Starting Morning Email Script (System Python)")
    print("📁 Make sure CSV files are in the __Load Files Go Here__ folder")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    # Use system Python to run the script
    try:
        subprocess.run([
            sys.executable, "morning_email.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Script stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try running: python3 morning_email.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 