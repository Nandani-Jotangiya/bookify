from datetime import datetime, UTC


FINE_PER_DAY = 10


def calculate_fine(due_date, return_date=None):
    """
    Calculate late days and fine amount.

    Returns:
        (late_days, fine_amount)
    """

    if return_date is None:
        return_date = datetime.now(UTC)

    if due_date is None:
        return 0, 0

    # Make timezone-aware if needed
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=UTC)

    if return_date <= due_date:
        return 0, 0

    late_days = (return_date - due_date).days

    fine_amount = late_days * FINE_PER_DAY

    return late_days, fine_amount