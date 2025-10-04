from flask import Blueprint, render_template, redirect, request

bp = Blueprint('DatosDeCampo', __name__)

@bp.route('/DatosDeCampo')
def datos_campo():
    return render_template('DatosDeCampo.html')
