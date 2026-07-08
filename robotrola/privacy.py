
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class RetentionPolicy:
    record_audio: bool = False
    record_video: bool = False
    cloud_upload: bool = False
    retention_days: int = 0

    def validate(self) -> None:
        if self.cloud_upload:
            raise ValueError("cloud_upload is disabled by default and requires explicit privacy review")
        if self.retention_days < 0:
            raise ValueError("retention_days must be >= 0")


def local_event(event_type: str, message: str) -> dict:
    return {"ts": datetime.now(timezone.utc).isoformat(), "event_type": event_type, "message": message}
