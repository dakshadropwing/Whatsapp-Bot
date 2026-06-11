"""
Endpoints routes — CRUD for external API endpoint configs.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

endpoints_bp = Blueprint("endpoints", __name__)


@endpoints_bp.get("/")
@jwt_required()
def list_endpoints():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@endpoints_bp.get("/<endpoint_id>")
@jwt_required()
def get_endpoint(endpoint_id: str):
    return jsonify({"endpoint": {"id": endpoint_id}}), 200


@endpoints_bp.post("/")
@jwt_required()
def create_endpoint():
    data = request.get_json(silent=True) or {}
    return jsonify({"id": "new", **data}), 201


@endpoints_bp.patch("/<endpoint_id>")
@jwt_required()
def update_endpoint(endpoint_id: str):
    data = request.get_json(silent=True) or {}
    return jsonify({"id": endpoint_id, "updated": True}), 200


@endpoints_bp.delete("/<endpoint_id>")
@jwt_required()
def delete_endpoint(endpoint_id: str):
    return jsonify({"deleted": True}), 200


@endpoints_bp.post("/<endpoint_id>/test")
@jwt_required()
def test_endpoint(endpoint_id: str):
    # TODO: EndpointService.test(endpoint_id)
    return jsonify({"id": endpoint_id, "success": True, "status_code": 200}), 200
