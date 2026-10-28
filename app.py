#!/usr/bin/env python3
"""
app.py
======
Entrypoint script for the Electric Vehicle (EV) Market Analysis web platform.
Usage:
    python3 app.py
"""

import os
from app import create_app

env_name = os.getenv("FLASK_ENV", "development")
app = create_app(env_name)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    print("\n" + "="*70)
    print(" ELECTRIC VEHICLE MARKET ANALYSIS — BI PLATFORM")
    print(f" Server running at: http://127.0.0.1:{port}/")
    print(f" Environment:       {env_name}")
    print(f" Debug mode:        {debug}")
    print("="*70 + "\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
