from flask import Blueprint, render_template, redirect, request

bp = Blueprint('VariablesDeInicio', __name__)

@bp.route('/VariablesDeInicio')
def variables_inicio():
    return render_template('VariablesDeInicio.html')
