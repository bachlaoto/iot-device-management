import json
import pytest
from unittest.mock import MagicMock

from utilities import validate_handshake_payload
from ws_client import WebSocketManager
from ui import AppUI


# Unit tests for validate_handshake_payload
def test_validate_handshake_payload_valid():
    payload = {
        "action": "handshake",
        "client_id": "test-client-001",
        "timestamp": "2026-05-20T12:00:00Z",
    }
    is_valid, error = validate_handshake_payload(payload)
    assert is_valid is True
    assert error is None


def test_validate_handshake_payload_missing_field():
    payload = {
        "action": "handshake",
        "client_id": "test-client-001",
        # missing timestamp
    }
    is_valid, error = validate_handshake_payload(payload)
    assert is_valid is False
    assert "timestamp" in error


def test_validate_handshake_payload_empty_field():
    payload = {
        "action": "handshake",
        "client_id": "",
        "timestamp": "2026-05-20T12:00:00Z",
    }
    is_valid, error = validate_handshake_payload(payload)
    assert is_valid is False
    assert "client_id" in error


def test_validate_handshake_payload_wrong_action():
    payload = {
        "action": "ping",
        "client_id": "test-client-001",
        "timestamp": "2026-05-20T12:00:00Z",
    }
    is_valid, error = validate_handshake_payload(payload)
    assert is_valid is False
    assert "action" in error


def test_validate_handshake_payload_not_dict():
    payload = "not-a-dict"
    is_valid, error = validate_handshake_payload(payload)
    assert is_valid is False
    assert "dictionary" in error


# WebSocketManager tests (unit + integration)
def test_ws_send_handshake_calls_ws_send():
    logger = MagicMock()
    ws = WebSocketManager(logger=logger)
    ws.ws_app = MagicMock()
    ws.connected = True

    payload = {"action": "handshake", "client_id": "test-client", "timestamp": "2026-05-20T00:00:00Z"}
    ws.send_handshake(payload)

    # ensure send called and payload matches
    assert ws.ws_app.send.call_count == 1
    raw = ws.ws_app.send.call_args[0][0]
    parsed = json.loads(raw)
    assert parsed == payload


def test_ws_send_handshake_validation_logs_on_invalid():
    logger = MagicMock()
    ws = WebSocketManager(logger=logger)
    ws.ws_app = MagicMock()
    ws.connected = True

    invalid_payload = {"action": "ping", "client_id": "id", "timestamp": "2026-05-20T00:00:00Z"}
    ws.send_handshake(invalid_payload)

    # should not send when invalid
    assert ws.ws_app.send.call_count == 0
    # logger should have been called with validation error
    assert logger.log.called
    last = logger.log.call_args_list[-1][0][0]
    assert "Handshake validation error" in last


def test_ws_on_open_auto_sends_handshake_and_content():
    logger = MagicMock()
    ws = WebSocketManager(logger=logger)
    ws.ws_app = MagicMock()
    # start disconnected
    ws.connected = False

    # simulate on_open -> should set connected True and auto-send handshake
    ws._on_open(None)

    assert ws.ws_app.send.call_count == 1
    raw = ws.ws_app.send.call_args[0][0]
    parsed = json.loads(raw)
    assert parsed.get("action") == "handshake"
    assert isinstance(parsed.get("client_id"), str) and parsed.get("client_id")
    assert isinstance(parsed.get("timestamp"), str) and parsed.get("timestamp")


# UI tests for send_handshake handler (lightweight)
def test_ui_send_handshake_malformed_json_logs():
    # create AppUI instance without running __init__ to avoid GUI creation
    app = AppUI.__new__(AppUI)
    app.logger = MagicMock()
    app.ws_manager = MagicMock()

    # simulate malformed JSON -> _parse_request_json returns None
    app._parse_request_json = lambda: None

    AppUI.send_handshake(app)

    assert app.logger.log.called
    last = app.logger.log.call_args_list[-1][0][0]
    assert "invalid json" in last.lower()


def test_ui_send_handshake_valid_calls_ws_manager():
    app = AppUI.__new__(AppUI)
    app.logger = MagicMock()
    app.ws_manager = MagicMock()

    payload = {"action": "handshake", "client_id": "ui-client", "timestamp": "2026-05-20T00:00:00Z"}
    app._parse_request_json = lambda: payload

    AppUI.send_handshake(app)

    app.ws_manager.send_handshake.assert_called_once_with(payload)

