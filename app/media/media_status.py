from enum import StrEnum


class MediaStatus(StrEnum):
    IN_QUEUE = "IN_QUEUE"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
