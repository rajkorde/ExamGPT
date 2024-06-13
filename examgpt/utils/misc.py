import datetime


def get_current_time() -> str:
    """Gets the current date and time as a string."""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    return str(timestamp)
