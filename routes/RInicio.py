from flask import Blueprint, redirect

bp = Blueprint("Inicio", __name__)

@bp.route("/")
def Inicio():
    return redirect("/VariablesDeInicio")
