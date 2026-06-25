"""
Unit tests for backend model definitions.
"""
import uuid
from datetime import datetime, timezone
from app.models.activity_log import ActivityLog
from app.models.agent_config import AgentConfig
from app.models.api_key import ApiKey
from app.models.encryption_metadata import EncryptionMetadata
from app.models.permission import Permission, roles_permissions
from app.models.system_setting import SystemSetting
from app.models.webhook_log import WebhookLog
from app.models.workflow_execution import WorkflowExecution


def test_activity_log_fields():
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    log = ActivityLog(
        organization_id=org_id,
        user_id=user_id,
        activity_type="user_login",
        description="User logged in successfully",
        metadata_={"ip": "127.0.0.1"},
    )
    assert log.organization_id == org_id
    assert log.user_id == user_id
    assert log.activity_type == "user_login"
    assert log.description == "User logged in successfully"
    assert log.metadata_ == {"ip": "127.0.0.1"}
    assert "user_login" in repr(log)


def test_agent_config_fields():
    agent_id = uuid.uuid4()
    config = AgentConfig(
        agent_id=agent_id,
        config_key="temperature",
        config_value="0.7",
        value_type="float",
    )
    assert config.agent_id == agent_id
    assert config.config_key == "temperature"
    assert config.config_value == "0.7"
    assert config.value_type == "float"
    assert "temperature" in repr(config)


def test_api_key_fields():
    org_id = uuid.uuid4()
    key = ApiKey(
        organization_id=org_id,
        name="Prod Key",
        key_hash="hashed_value",
        prefix="pk_123",
        is_active=True,
    )
    assert key.organization_id == org_id
    assert key.name == "Prod Key"
    assert key.key_hash == "hashed_value"
    assert key.prefix == "pk_123"
    assert key.is_active is True
    assert "Prod Key" in repr(key)


def test_encryption_metadata_fields():
    meta = EncryptionMetadata(
        key_id="key-v1",
        algorithm="AES-GCM",
        rotation_count=1,
    )
    assert meta.key_id == "key-v1"
    assert meta.algorithm == "AES-GCM"
    assert meta.rotation_count == 1
    assert "key-v1" in repr(meta)


def test_permission_fields():
    perm = Permission(
        name="agents:write",
        description="Create and update agents",
    )
    assert perm.name == "agents:write"
    assert perm.description == "Create and update agents"
    assert "agents:write" in repr(perm)


def test_system_setting_fields():
    setting = SystemSetting(
        key="maintenance_mode",
        value="false",
        description="Put platform in maintenance mode",
        is_public=True,
    )
    assert setting.key == "maintenance_mode"
    assert setting.value == "false"
    assert setting.description == "Put platform in maintenance mode"
    assert setting.is_public is True
    assert "maintenance_mode" in repr(setting)


def test_webhook_log_fields():
    org_id = uuid.uuid4()
    endpoint_id = uuid.uuid4()
    log = WebhookLog(
        organization_id=org_id,
        endpoint_config_id=endpoint_id,
        url="https://api.example.com/webhook",
        event_type="message.received",
        status_code=200,
        request_payload={"event": "test"},
        response_payload={"status": "ok"},
        processing_time_ms=120,
    )
    assert log.organization_id == org_id
    assert log.endpoint_config_id == endpoint_id
    assert log.url == "https://api.example.com/webhook"
    assert log.event_type == "message.received"
    assert log.status_code == 200
    assert log.request_payload == {"event": "test"}
    assert log.response_payload == {"status": "ok"}
    assert log.processing_time_ms == 120
    assert "message.received" in repr(log)


def test_workflow_execution_fields():
    workflow_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    exec_ = WorkflowExecution(
        workflow_id=workflow_id,
        conversation_id=conv_id,
        status="completed",
        input_data={"param": 1},
        output_data={"result": "success"},
    )
    assert exec_.workflow_id == workflow_id
    assert exec_.conversation_id == conv_id
    assert exec_.status == "completed"
    assert exec_.input_data == {"param": 1}
    assert exec_.output_data == {"result": "success"}
    assert "completed" in repr(exec_)
