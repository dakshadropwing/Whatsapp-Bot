"""
Script to seed the database with initial development data.
"""
from __future__ import annotations

import sys
import os
from passlib.hash import bcrypt

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.whatsapp_account import WhatsAppAccount
from app.models.ai_agent import AIAgent
from app.models.endpoint_config import EndpointConfig


def seed_database() -> None:
    app = create_app()
    with app.app_context():
        print("🌱 Seeding database with initial data...")

        # ── 1. Create Default Organization ──────────────────────────────────
        org = db.session.query(Organization).filter_by(slug="default").first()
        if not org:
            org = Organization(
                name="Demo Organization",
                slug="default",
                description="Default demo tenant organization",
                plan="starter",
                max_users=10,
                max_agents=5,
            )
            db.session.add(org)
            db.session.flush()
            print(f"   Created default organization: {org.name} ({org.id})")
        else:
            print(f"   Default organization already exists: {org.id}")

        # ── 2. Create Default Roles ──────────────────────────────────────────
        roles_to_create = [
            ("superadmin", "Super Administrator with full platform access"),
            ("admin", "Organization administrator"),
            ("agent", "Support agent"),
            ("user", "Regular staff user"),
        ]
        created_roles = {}
        for role_name, desc in roles_to_create:
            role = db.session.query(Role).filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=desc)
                db.session.add(role)
                db.session.flush()
                print(f"   Created role: {role_name}")
            created_roles[role_name] = role

        # ── 3. Create Default Users ──────────────────────────────────────────
        users_to_create = [
            ("admin@dev.local", "admin", "Admin User", "superadmin"),
            ("agent@dev.local", "agent", "Agent User", "agent"),
        ]
        for email, username, full_name, role_name in users_to_create:
            user = db.session.query(User).filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    username=username,
                    full_name=full_name,
                    password_hash=bcrypt.hash("password123"),
                    is_active=True,
                    is_superadmin=(role_name == "superadmin"),
                    organization_id=org.id,
                    role_id=created_roles[role_name].id,
                )
                db.session.add(user)
                print(f"   Created user: {email}")

        # ── 4. Create Default WhatsApp Account ──────────────────────────────
        wa_account = db.session.query(WhatsAppAccount).filter_by(organization_id=org.id).first()
        if not wa_account:
            wa_account = WhatsAppAccount(
                organization_id=org.id,
                phone_number_id="1234567890",
                waba_id="waba_demo_123",
                access_token="access_token_demo_xyz",
                verify_token="verify_token_demo_abc",
                is_active=True,
            )
            db.session.add(wa_account)
            print(f"   Created default WhatsApp Account configuration.")

        # ── 5. Create Default AI Agents ─────────────────────────────────────
        agents_to_create = [
            ("Aria", "support", "You are Aria, a friendly customer support AI agent."),
            ("Booker", "appointment", "You are Booker, a helpful booking assistant AI agent."),
            ("Hunter", "lead", "You are Hunter, a sales lead qualification AI agent."),
        ]
        for name, role_type, prompt in agents_to_create:
            agent = db.session.query(AIAgent).filter_by(organization_id=org.id, name=name).first()
            if not agent:
                agent = AIAgent(
                    organization_id=org.id,
                    name=name,
                    role_type=role_type,
                    system_prompt=prompt,
                    provider="gemini",
                    model_name="gemini-2.5-flash",
                    is_active=True,
                )
                db.session.add(agent)
                print(f"   Created AI Agent: {name} ({role_type})")

        # ── 6. Create Demo Custom Endpoint Config ──────────────────────────
        endpoint = db.session.query(EndpointConfig).filter_by(organization_id=org.id, name="order_status").first()
        if not endpoint:
            endpoint = EndpointConfig(
                organization_id=org.id,
                name="order_status",
                description="Demo order status checker webhook",
                url="https://api.mockaroo.com/api/order_status",
                method="POST",
                headers={"Authorization": "Bearer demo_api_key"},
                is_active=True,
            )
            db.session.add(endpoint)
            print(f"   Created demo EndpointConfig: order_status")

        db.session.commit()
        print("🎉 Database seeding complete!")


if __name__ == "__main__":
    seed_database()
