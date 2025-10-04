from flask import Blueprint, render_template, redirect, request
from utils.conexion import Session
from utils import tools
from model import MUsers

bp = Blueprint("Auth", __name__)


@bp.route("/Login", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        try:
            data: dict = request.get_json()
            username: str = data["username"]
            password: str = data["password"]
            user = MUsers.GetUserLogin(username, password)
            if user is None:
                return tools.msg(1, "Usuario o contraseña incorrectos.")
            Session["iduser"] = user["iduser"]
            return tools.msg(redirect="/")
        except Exception as e:
            return tools.msg(1, e, log=True)
    return render_template("Login.html")


@bp.route("/Logout", methods=["GET", "POST"])
def Logout():
    Session.clear()
    if request.method == "GET":
        return redirect("/Login")
    return {"status": 0, "redirect__": "/Login"}


@bp.route("/Register", methods=["GET", "POST"])
def Register():
    if request.method == "POST":
        try:
            data: dict = request.get_json()
            username: str = data["username"]
            password: str = data["password"]
            confirm_password: str = data["confirm_password"]
            if password != confirm_password:
                return tools.msg(1, "Las contraseñas no coinciden")

            user = MUsers.GetUserByName(username)
            if user is not None:
                return tools.msg(1, "Este nombre de usuario esta ocupado")

            result = MUsers.RegUser(username, password)
            Session["iduser"] = result["iduser"]
            return tools.msg(redirect="/")
        except Exception as e:
            return tools.msg(1, e, log=True)
    return render_template("Register.html")
