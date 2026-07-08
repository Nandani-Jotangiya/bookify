from enum import Enum


class NotificationType(str, Enum):
    BOOK_ISSUED = "book_issued"
    BOOK_REQUESTED = "book_requested"
    BOOK_RETURNED = "book_returned"
    REQUEST_APPROVED = "request_approved"
    REQUEST_REJECTED = "request_rejected"

    # BOOK_DUE = "book_due"

    # BOOK_OVERDUE = "book_overdue"

    # FINE_GENERATED = "fine_generated"
