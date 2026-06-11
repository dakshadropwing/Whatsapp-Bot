"""
Settings routes — get/update organization settings.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

settings_bp = Blueprint("settings", __name__)


@settings_bp.get("/")
@jwt_required()
def get_settings():
    # TODO: SettingsService.get(org_id)
    return jsonify({
        "whatsapp": {"phone_number_id": "", "webhook_verify_token": ""},
        "ai": {"default_model": "gemini-pro", "max_tokens": 2048},
        "security": {"session_timeout_minutes": 30, "require_2fa": False},
        "notifications": {"email_alerts": True, "slack_webhook": ""},
    }), 200


@settings_bp.patch("/")
@jwt_required()
def update_settings():
    data = request.get_json(silent=True) or {}
    # TODO: SettingsService.update(org_id, data)
    return jsonify({"updated": True}), 200


@settings_bp.get("/<section>")
@jwt_required()
def get_settings_section(section: str):
    # TODO: SettingsService.get_section(org_id, section)
    return jsonify({"section": section, "data": {}}), 200
