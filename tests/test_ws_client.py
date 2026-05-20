import unittest
from unittest.mock import MagicMock, patch
from ws_client import WebSocketManager

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

if __name__ == "__main__":
    unittest.main()