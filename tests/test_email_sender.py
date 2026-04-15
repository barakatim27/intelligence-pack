import unittest
from unittest.mock import MagicMock, patch

from delivery.email_sender import EmailDeliveryError, send_email_digest


class EmailSenderTests(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "SENDER_EMAIL": "sender@example.com",
            "SENDER_PASSWORD": "secret",
            "RECIPIENT_EMAIL": "recipient@example.com",
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
        },
        clear=True,
    )
    @patch("delivery.email_sender.smtplib.SMTP")
    def test_send_email_digest_uses_smtp_tls_login_and_send(self, smtp_mock: MagicMock) -> None:
        send_email_digest("digest body")

        smtp_mock.assert_called_once_with("smtp.example.com", 587, timeout=30)
        server = smtp_mock.return_value.__enter__.return_value
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("sender@example.com", "secret")
        server.send_message.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    def test_send_email_digest_raises_when_env_missing(self) -> None:
        with self.assertRaises(ValueError):
            send_email_digest("digest body")

    @patch.dict(
        "os.environ",
        {
            "SENDER_EMAIL": "sender@example.com",
            "SENDER_PASSWORD": "secret",
            "RECIPIENT_EMAIL": "recipient@example.com",
        },
        clear=True,
    )
    @patch("delivery.email_sender.smtplib.SMTP", side_effect=OSError("network failure"))
    def test_send_email_digest_wraps_transport_errors(self, _: MagicMock) -> None:
        with self.assertRaises(EmailDeliveryError):
            send_email_digest("digest body")


if __name__ == "__main__":
    unittest.main()
