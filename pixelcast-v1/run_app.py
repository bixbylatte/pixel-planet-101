#!/usr/bin/env python3
import subprocess
import sys
import os

# Set environment variables to skip Streamlit's email prompt
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Run streamlit with the app
subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.port', '8501', '--server.address', '0.0.0.0'])


