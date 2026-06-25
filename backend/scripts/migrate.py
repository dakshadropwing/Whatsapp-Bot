"""
Programmatic wrapper to run Alembic database migrations.
Usage:
    python scripts/migrate.py [upgrade|downgrade] [revision]
"""
from __future__ import annotations

import argparse
import os
import sys

from alembic.config import Config
from alembic import command

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_migrations(action: str, target: str) -> None:
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ini_path = os.path.join(backend_dir, "alembic.ini")
    
    # Instantiate Alembic configuration
    alembic_cfg = Config(ini_path)
    # Set the working directory to backend
    alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "migrations"))

    print(f"⚙️ Running Alembic migration '{action}' to target '{target}'...")

    try:
        if action == "upgrade":
            command.upgrade(alembic_cfg, target)
        elif action == "downgrade":
            command.downgrade(alembic_cfg, target)
        print("🎉 Migration completed successfully!")
    except Exception as exc:
        print(f"❌ Migration failed: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Alembic migrations.")
    parser.add_argument("action", choices=["upgrade", "downgrade"], default="upgrade", nargs="?", help="Action to perform")
    parser.add_argument("target", default="head", nargs="?", help="Target revision ID or 'head'")
    args = parser.parse_args()

    run_migrations(args.action, args.target)


if __name__ == "__main__":
    main()
