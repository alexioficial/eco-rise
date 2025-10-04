from flask import Blueprint, render_template, request
from utils import tools

bp = Blueprint('VariablesDeInicio', __name__)

@bp.route('/VariablesDeInicio')
def variables_inicio():
    return render_template('VariablesDeInicio.html')

@bp.route('/SubirDatos', methods = ['POST'])
def SubirDatos():
    try:
        _data: dict = request.get_json()
        
        return tools.msg()
    except Exception as e:
        return tools.msg_err(e)