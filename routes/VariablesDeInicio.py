from flask import Blueprint, render_template, request
from utils import tools

bp = Blueprint('VariablesDeInicio', __name__)

@bp.route('/VariablesDeInicio')
def initial_variables():
    return render_template('VariablesDeInicio.html')

@bp.route('/UploadData', methods = ['POST'])
def UploadData():
    try:
        _data: dict = request.get_json()
        
        return tools.msg()
    except Exception as e:
        return tools.msg_err(e)