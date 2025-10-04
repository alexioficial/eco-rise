from flask import Blueprint, render_template, redirect, request

bp = Blueprint('Principal', __name__)

@bp.route('/Principal')
def Principal():
    return render_template('Principal.html')