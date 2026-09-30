#!/usr/bin/env python3
"""
Root setup entrypoint that forwards directly to projects/job-search/setup.py.
Allows users who clone the repository to run `python3 setup.py` from the root.
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_SETUP = os.path.join(BASE_DIR, "projects", "job-search", "setup.py")

if not os.path.exists(PROJECT_SETUP):
    print(f"Error: Could not find setup script at {PROJECT_SETUP}")
    sys.exit(1)

cmd = [sys.executable, PROJECT_SETUP] + sys.argv[1:]
sys.exit(subprocess.call(cmd))
