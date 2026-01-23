import requests
from datetime import datetime
from src.config import settings


def _send(text: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()


# Service Alert (for hosted services, cron jobs, deployments, etc.)
def send_service_alert(service_name: str, status: str, message: str = ""):
    """
    status: UP, DOWN, RESTARTED, DEPLOYED, HEALTHY, UNHEALTHY
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = (
        f"🔔 *Service Alert*\n\n"
        f"*Service:* `{service_name}`\n"
        f"*Status:* `{status}`\n"
        f"*Time:* `{timestamp}`\n"
    )

    if message:
        text += f"\n*Info:*\n{message}"

    return _send(text)


# Android Error Alert (for crash logs, exceptions, stack traces)
def send_android_error(app_name: str, error_type: str, error_message: str, stacktrace: str = ""):
    """
    error_type: NullPointerException, ANR, NetworkError, etc.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = (
        f"🚨 *Android App Error*\n\n"
        f"*App:* `{app_name}`\n"
        f"*Type:* `{error_type}`\n"
        f"*Time:* `{timestamp}`\n\n"
        f"*Message:*\n`{error_message}`"
    )

    if stacktrace:
        # limit length so Telegram doesn't reject it
        short_trace = stacktrace[:3500]
        text += f"\n\n*Stacktrace:*\n```{short_trace}```"

    return _send(text)
