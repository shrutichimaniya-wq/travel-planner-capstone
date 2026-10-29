"""
Vercel Serverless Function entry point.
Exposes the Flask WSGI application instance.
"""

import sys
import os

# Ensure the root directory is on the Python module search path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Vercel WSGI entry point
# Flask `app` serves HTTP requests
