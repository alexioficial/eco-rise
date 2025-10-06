from typing import Union, Any
from datetime import datetime
from bson import ObjectId
from utils.conexion import log_col, GenerateUuid
import sys


def write_log(msg: Union[str, Exception] = "", status: Union[int, str] = 0):
    """
    Stores a log message in the database.

    Args:
        msg: Message to write to log
        status: Log status (0: success, 1 or 'error': error, 2 or 'warning': warning)
    """
    is_error = (
        status == 1 or str(status).lower() == "error" or isinstance(msg, Exception)
    )
    is_warning = status == 2 or str(status).lower() == "warning"

    if is_error:
        log_type = "error"
        color = "\033[91m"  # Red
    elif is_warning:
        log_type = "warning"
        color = "\033[93m"  # Orange
    else:
        log_type = "success"
        color = "\033[92m"  # Green

    timestamp = datetime.now()
    message = str(msg)

    # Create log document
    log_doc = {
        "log_id": GenerateUuid(),
        "timestamp": timestamp,
        "type": log_type,
        "message": f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n",
    }

    # Insert into database
    log_col.insert_one(log_doc)

    # Keep console output for debugging
    formatted_message = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    if color:
        print(f"{color}{formatted_message}\033[0m", end="")
    else:
        print(formatted_message, end="")


def msg(
    status: int = 0, msg: Union[str, Exception] = "", log: bool = False, **kwargs
) -> dict:
    if status == 1:  # error
        print("\033[91m" + str(msg) + "\033[0m")

    if log:
        write_log(msg, status)

    # Convert Exception to string for JSON serialization
    msg_str = str(msg) if isinstance(msg, Exception) else msg

    return {"status": status, "msg": msg_str, **kwargs}


def msg_err(exception: Exception):
    return msg(1, exception, log=True)


def parse_ids(data: Union[dict, list]):
    if isinstance(data, dict):
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in data.items()}
    return [parse_ids(item) for item in data]


def abs_path(relative_path: str):
    relative_path = relative_path.replace("\\", "/")
    relative_path = (
        ("/" + relative_path) if not relative_path.startswith("/") else relative_path
    )
    return sys.path[0] + relative_path


def t_int(value: Any):
    try:
        return int(value)
    except Exception:
        return 0
