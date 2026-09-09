"""WSGI entry point for Gunicorn."""
from app.factory import create_app

app = create_app()

import os
if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", 5001))
    app.run(host="0.0.0.0", port=port)
