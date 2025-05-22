import threading
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import ActivityLog, User
from database.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActivityMonitor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.check_interval = 300  # 5 minutes
        self.suspicious_threshold = 50  # actions per time window
        self.time_window = 3600  # 1 hour in seconds

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Activity monitoring started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            logger.info("Activity monitoring stopped")

    def _monitor_loop(self):
        while self.running:
            try:
                self._check_suspicious_activity()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
            time.sleep(self.check_interval)

    def _check_suspicious_activity(self):
        db = SessionLocal()
        try:
            # Get current time and time window start
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.time_window)

            # Get all users
            users = db.query(User).all()
            
            for user in users:
                # Count actions in the time window
                action_count = db.query(ActivityLog).filter(
                    ActivityLog.user_id == user.id,
                    ActivityLog.timestamp >= window_start,
                    ActivityLog.timestamp <= now
                ).count()

                # If action count exceeds threshold, mark user as monitored
                if action_count > self.suspicious_threshold:
                    if not user.is_monitored:
                        user.is_monitored = True
                        logger.warning(f"User {user.username} marked as monitored due to suspicious activity")
                        db.commit()
        finally:
            db.close()

# Create a global instance of the monitor
activity_monitor = ActivityMonitor()

def start_monitoring():
    activity_monitor.start()

def stop_monitoring():
    activity_monitor.stop()

def log_activity(db: Session, user_id: int, action: str, entity_type: str, entity_id: int, details: str = None):
    """Log a user activity"""
    log_entry = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.add(log_entry)
    db.commit()
    return log_entry 