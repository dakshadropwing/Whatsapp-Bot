"""
CLI script to create a superadmin user.
Usage:
    python scripts/create_superadmin.py --email admin@dev.local --username admin --password supersecret
"""
from __future__ import annotations

import argparse
import sys
import uuid
from werkzeug.security import generate_password_hash

# Add backend directory to path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User


def create_superadmin(email: str, username: str, password_raw: str) -> None:
    app = create_app()
    with app.app_context():
        # Ensure we have a default organization
        org = db.session.query(Organization).filter_by(slug="default").first()
        if not org:
            org = Organization(
                name="Default Org",
                slug="default",
                description="Default Organization",
            )
            db.session.add(org)
            db.session.flush()
            print(f"Created default organization: {org.id}")

        # Ensure we have a Superadmin role
        role = db.session.query(Role).filter_by(name="superadmin").first()
        if not role:
            role = Role(
                name="superadmin",
                description="Super Administrator role with full access",
            )
            db.session.add(role)
            db.session.flush()
            print(f"Created superadmin role: {role.id}")

        # Check if user already exists
        existing_user = db.session.query(User).filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return

        # Hash password and create user
        password_hash = generate_password_hash(password_raw)
        user = User(
            email=email,
            username=username,
            full_name="Super Admin",
            password_hash=password_hash,
            is_active=True,
            is_superadmin=True,
            email_verified=True,
            organization_id=org.id,
            role_id=role.id,
        )
        db.session.add(user)
        db.session.commit()
        print(f"🎉 Successfully created superadmin user {username} ({email})!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a superadmin user.")
    parser.add_argument("--email", default="admin@dev.local", help="Superadmin email")
    parser.add_argument("--username", default="admin", help="Superadmin username")
    parser.add_argument("--password", default="admin123", help="Superadmin password")
    args = parser.parse_args()

    create_superadmin(args.email, args.username, args.password)


if __name__ == "__main__":
    main()
