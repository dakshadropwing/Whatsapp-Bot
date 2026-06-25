"""
Settings routes — get/update organization settings.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.attributes import flag_modified

from app.extensions import db
from app.models.organization import Organization

settings_bp = Blueprint("settings", __name__)

DEFAULT_SETTINGS = {
    "whatsapp": {"phone_number_id": "", "webhook_verify_token": ""},
    "ai": {"default_model": "gemini-pro", "max_tokens": 2048},
    "security": {"session_timeout_minutes": 30, "require_2fa": False},
    "notifications": {"email_alerts": True, "slack_webhook": ""},
}


@settings_bp.get("/")
@jwt_required()
def get_settings():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    org = db.session.get(Organization, uuid.UUID(org_id))
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    # Merge database settings with defaults
    current_settings = dict(DEFAULT_SETTINGS)
    if org.settings:
        for section, config in org.settings.items():
            if section in current_settings and isinstance(config, dict):
                current_settings[section].update(config)
            else:
                current_settings[section] = config

    return jsonify(current_settings), 200


@settings_bp.patch("/")
@jwt_required()
def update_settings():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    org = db.session.get(Organization, uuid.UUID(org_id))
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    data = request.get_json(silent=True) or {}

    if not org.settings:
        org.settings = {}

    # Update sections
    for section, config in data.items():
        if isinstance(config, dict):
            if section not in org.settings or not isinstance(org.settings[section], dict):
                org.settings[section] = {}
            org.settings[section].update(config)
        else:
            org.settings[section] = config

    # Mark modified to ensure SQLAlchemy updates JSONB field
    flag_modified(org, "settings")
    db.session.commit()

    return jsonify({"updated": True, "settings": org.settings}), 200


@settings_bp.get("/<section>")
@jwt_required()
def get_settings_section(section: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    org = db.session.get(Organization, uuid.UUID(org_id))
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    # Get from org settings or default settings
    section_settings = {}
    if org.settings and section in org.settings:
        section_settings = org.settings[section]
    elif section in DEFAULT_SETTINGS:
        section_settings = DEFAULT_SETTINGS[section]

    return jsonify({"section": section, "data": section_settings}), 200
