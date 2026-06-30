from datetime import datetime

# Library fine policy
FINE_PER_DAY = 10.0


def calculate_fine(issued_book):
    """
    Calculate late days and fine amount for an issued book.

    Business Rules:
    ---------------
    1. If the book has not been returned yet:
       - Late Days = 0
       - Fine = 0

    2. If the book is returned on or before the due date:
       - Late Days = 0
       - Fine = 0

    3. If the book is returned after the due date:
       - Late Days = Difference between return date and due date
       - Fine = Late Days × FINE_PER_DAY

    Parameters:
    -----------
    issued_book : IssuedBook
        SQLAlchemy IssuedBook object

    Returns:
    --------
    tuple
        (late_days, fine_amount)
    """

    # Book not returned yet
    if issued_book.return_date is None:
        return 0, 0.0

    # Returned on time
    if issued_book.return_date.date() <= issued_book.due_date.date():
        return 0, 0.0

    # Calculate late days
    late_days = (issued_book.return_date.date() - issued_book.due_date.date()).days

    # Calculate fine
    fine_amount = late_days * FINE_PER_DAY

    return late_days, fine_amount