from typing import Union, Any
from datetime import datetime
from bson import ObjectId
from utils.conexion import log_col, GenerarUuid
import sys


def escribir_log(msg: Union[str, Exception] = "", status: Union[int, str] = 0):
    """
    Almacena un mensaje de log en la base de datos.

    Args:
        msg: Mensaje a escribir en el log
        status: Estado del log (0: éxito, 1 o 'error': error, 2 o 'warning': advertencia)
    """
    es_error = (
        status == 1 or str(status).lower() == "error" or isinstance(msg, Exception)
    )
    es_warning = status == 2 or str(status).lower() == "warning"

    if es_error:
        tipo = "error"
        color = "\033[91m"  # Rojo
    elif es_warning:
        tipo = "warning"
        color = "\033[93m"  # Naranja
    else:
        tipo = "exito"
        color = "\033[92m"  # Verde

    timestamp = datetime.now()
    mensaje = str(msg)

    # Crear documento de log
    log_doc = {
        "idlog": GenerarUuid(),
        "fecha_hora": timestamp,
        "tipo": tipo,
        "mensaje": f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n",
    }

    # Insertar en la base de datos
    log_col.insert_one(log_doc)

    # Mantener la salida en consola para debugging
    mensaje_formateado = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n"
    if color:
        print(f"{color}{mensaje_formateado}\033[0m", end="")
    else:
        print(mensaje_formateado, end="")


def msg(
    status: int = 0, msg: Union[str, Exception] = "", log: bool = False, **kwargs
) -> dict:
    if status == 1:  # error
        print("\033[91m" + str(msg) + "\033[0m")

    if log:
        escribir_log(msg, status)

    # Convert Exception to string for JSON serialization
    msg_str = str(msg) if isinstance(msg, Exception) else msg

    return {"status": status, "msg": msg_str, **kwargs}


def msg_err(exception: Exception):
    return msg(1, exception, log=True)


def parse_ids(datos: Union[dict, list]):
    if isinstance(datos, dict):
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in datos.items()}
    return [parse_ids(item) for item in datos]


def ruta_abs(ruta_relativa: str):
    ruta_relativa = ruta_relativa.replace("\\", "/")
    ruta_relativa = (
        ("/" + ruta_relativa) if not ruta_relativa.startswith("/") else ruta_relativa
    )
    return sys.path[0] + ruta_relativa


def t_int(valor: Any):
    try:
        return int(valor)
    except Exception:
        return 0
