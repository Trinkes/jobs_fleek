from enum import StrEnum


class MediaStatus(StrEnum):
    ERROR = "ERROR"
    IN_QUEUE = "IN_QUEUE"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
