#!/usr/bin/env python3
"""
WSGI entry point untuk production deployment
"""

import os
from app import app

# Create application instance for WSGI
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Hybrid VPN API on port {port}")
    app.run(host='0.0.0.0', port=port) 