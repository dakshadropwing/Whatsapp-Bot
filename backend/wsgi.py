"""WSGI entry point for Gunicorn."""
from app.factory import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
