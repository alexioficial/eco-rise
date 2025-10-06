from flask import Blueprint, render_template

bp = Blueprint('DatosDeCampo', __name__)

@bp.route('/DatosDeCampo')
def field_data():
    return render_template('DatosDeCampo.html')
