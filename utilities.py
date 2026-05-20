from datetime import datetime
from typing import Optional, Tuple

# Handshake configuration
HANDSHAKE_REQUIRED_FIELDS = ["action", "client_id", "timestamp"]


DEFAULT_COMMANDS = [
    {
        "name": "Ping",
        "payload": {
            "action": "ping",
            "timestamp": "2026-03-27T12:00:00Z",
        },
    },
    {
        "name": "Login",
        "payload": {
            "action": "login",
            "username": "demo_user",
            "token": "replace-me",
        },
    },
    {
        "name": "Subscribe",
        "payload": {
            "action": "subscribe",
            "channel": "events",
        },
    },
    {
        "name": "Echo",
        "payload": {
            "action": "echo",
            "message": "hello from tkinter client",
        },
    },
    {
        "name": "HTTP POST sample",
        "payload": {
            "method": "POST",
            "path": "/api/commands",
            "headers": {
                "Content-Type": "application/json",
            },
            "body": {
                "action": "status",
            },
            "timeout": 10,
        },
    },
    {
        "name": "Handshake",
        "payload": {
            "action": "handshake",
            "client_id": "replace-with-client-id",
            "timestamp": "2026-05-20T00:00:00Z",
        },
    },
]


def validate_handshake_payload(payload: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate handshake payload structure and required fields.
    
    Args:
        payload: Dictionary to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not isinstance(payload, dict):
        return False, "Handshake payload must be a dictionary"
    
    for field in HANDSHAKE_REQUIRED_FIELDS:
        if field not in payload:
            return False, f"Missing required field: {field}"
        
        value = payload[field]
        if not isinstance(value, str) or not value.strip():
            return False, f"Field '{field}' must be a non-empty string"
    
    if payload.get("action") != "handshake":
        return False, "Field 'action' must be 'handshake'"
    
    return True, None


class AppLogger:
    def __init__(self, callback) -> None:
        self.callback = callback

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.callback(f"[{timestamp}] {message}\n")
