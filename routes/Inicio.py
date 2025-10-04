from flask import Blueprint, redirect

bp = Blueprint('Inicio', __name__)

@bp.route('/')
def inicio():
    return redirect('/Principal')