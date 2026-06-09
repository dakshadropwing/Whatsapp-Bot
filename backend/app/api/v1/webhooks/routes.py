"""
Webhooks routes — receiver for Meta/WhatsApp inbound webhooks.
"""
from flask import Blueprint, jsonify

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.get("/")
def health():
    return jsonify({"status": "active"}), 200
