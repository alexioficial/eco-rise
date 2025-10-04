from flask import Blueprint, redirect, request
import utils.tools as tools
from utils.conexion import Session

bp = Blueprint("Inicio", __name__)


@bp.before_app_request
def validate_login():
    MSG_LOGIN_REQ = f"{request.environ.get('HTTP_X_REAL_IP', request.remote_addr)} tried to access {request.path} without logging in"
    EXCLUDED_PATHS = [
        "/static",
        "/Login",
        "/Register",
        "/AdminLogin",
        "/test",
        "/favicon.ico",
        "/SecurityCheck",
        "/.well-known/appspecific/com.chrome.devtools.json",
    ]
    if not any(request.path.startswith(path) for path in EXCLUDED_PATHS):
        if request.method == "POST" and "iduser" not in Session:
            tools.escribir_log(MSG_LOGIN_REQ, "warning")
            return tools.msg(1, "Login required", redirect="/Login")
        elif not Session.get("iduser") and request.method == "GET":
            tools.escribir_log(MSG_LOGIN_REQ, "warning")
            return redirect("/Login")


@bp.route("/")
def Inicio():
    if Session.get("iduser") is None:
        return redirect("/Login")
    return redirect("/VariablesDeInicio")


@bp.route("/SecurityCheck", methods=["POST"])
def SecurityCheck():
    try:
        data = request.get_json()
        const_iduser = data["const_iduser"]
        input_iduser = data["input_iduser"]
        real_iduser = Session["iduser"]
        if (const_iduser != input_iduser) or (const_iduser != real_iduser):
            Session.clear()
            return tools.msg(1, "Security check failed", redirect__="/Login")
        return tools.msg()
    except Exception as e:
        return tools.msg_err(e)
