import time
from .models import BroadcastLog
from .extensions import db


def send_broadcast(bot, broadcast, subscribers, telegram_service):
    sent = 0
    failed = 0

    for sub in subscribers:
        ok, error = telegram_service.send_message(sub.telegram_id, broadcast.text)

        log = BroadcastLog(
            status="delivered" if ok else "failed",
            error=error,
            subscriber_id=sub.id,
            broadcast_id=broadcast.id
        )

        db.session.add(log)

        if ok:
            sent += 1
        else:
            failed += 1

        time.sleep(0.05)

    db.session.commit()

    return sent, failed