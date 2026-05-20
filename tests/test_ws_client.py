import unittest
from unittest.mock import MagicMock, patch
from ws_client import WebSocketManager
from utilities import validate_handshake_payload

class TestWebSocketManager(unittest.TestCase):

    @patch("ws_client.WebSocketApp")
    def test_send_handshake(self, MockWebSocketApp):
        logger = MagicMock()
        ws_manager = WebSocketManager(logger=logger)
        ws_manager.ws_app = MockWebSocketApp()
        ws_manager.connected = True

        payload = {"action": "handshake", "client_id": "test-client", "timestamp": "2026-05-20T00:00:00Z"}
        ws_manager.send_handshake(payload)

        ws_manager.ws_app.send.assert_called_once_with('{"action": "handshake", "client_id": "test-client", "timestamp": "2026-05-20T00:00:00Z"}')

    @patch("ws_client.WebSocketApp")
    def test_auto_handshake_on_open(self, MockWebSocketApp):
        logger = MagicMock()
        ws_manager = WebSocketManager(logger=logger)
        ws_manager.ws_app = MockWebSocketApp()

        with patch.object(ws_manager, "send_handshake") as mock_send_handshake:
            ws_manager._on_open(None)
            mock_send_handshake.assert_called_once()

    def test_validate_handshake_payload_valid(self):
        """Test validation of valid handshake payload."""
        payload = {
            "action": "handshake",
            "client_id": "test-client-001",
            "timestamp": "2026-05-20T12:00:00Z"
        }
        is_valid, error_msg = validate_handshake_payload(payload)
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)

    def test_validate_handshake_payload_missing_field(self):
        """Test validation fails when required field is missing."""
        payload = {
            "action": "handshake",
            "client_id": "test-client-001"
            # Missing timestamp
        }
        is_valid, error_msg = validate_handshake_payload(payload)
        self.assertFalse(is_valid)
        self.assertIn("timestamp", error_msg)

    def test_validate_handshake_payload_empty_field(self):
        """Test validation fails when field value is empty."""
        payload = {
            "action": "handshake",
            "client_id": "",
            "timestamp": "2026-05-20T12:00:00Z"
        }
        is_valid, error_msg = validate_handshake_payload(payload)
        self.assertFalse(is_valid)
        self.assertIn("client_id", error_msg)

    def test_validate_handshake_payload_wrong_action(self):
        """Test validation fails when action is not 'handshake'."""
        payload = {
            "action": "ping",
            "client_id": "test-client-001",
            "timestamp": "2026-05-20T12:00:00Z"
        }
        is_valid, error_msg = validate_handshake_payload(payload)
        self.assertFalse(is_valid)
        self.assertIn("action", error_msg)

    def test_validate_handshake_payload_not_dict(self):
        """Test validation fails when payload is not a dictionary."""
        payload = "not a dict"
        is_valid, error_msg = validate_handshake_payload(payload)
        self.assertFalse(is_valid)
        self.assertIn("dictionary", error_msg)

    @patch("ws_client.WebSocketApp")
    def test_send_handshake_validates_payload(self, MockWebSocketApp):
        """Test send_handshake validates payload before sending."""
        logger = MagicMock()
        ws_manager = WebSocketManager(logger=logger)
        ws_manager.ws_app = MockWebSocketApp()
        ws_manager.connected = True

        # Try to send invalid payload
        invalid_payload = {
            "action": "ping",  # Wrong action
            "client_id": "test-client",
            "timestamp": "2026-05-20T00:00:00Z"
        }
        ws_manager.send_handshake(invalid_payload)

        # Verify logger was called with validation error
        logger.log.assert_called()
        log_call = logger.log.call_args_list[-1][0][0]
        self.assertIn("validation error", log_call)

if __name__ == "__main__":
    unittest.main()