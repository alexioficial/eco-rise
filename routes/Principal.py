from flask import Blueprint, render_template, request
from utils import tools
from utils.ai.tools import save_page_screenshot
# from utils.ai.main import client, execute_tool_call

bp = Blueprint('Principal', __name__)

@bp.route('/Principal')
def Principal():
    return render_template('Principal.html')

@bp.route('/Calculate', methods = ['POST'])
def Calculate():
    try:
        data = request.get_json()

        _ancho: float = float(data['ancho'])
        _alto: float = float(data['alto'])
        _tipo_planta: str = data['tipo_planta']
        _lat: str = data['lat']
        _lng: str = data['lng']

        save_page_screenshot()

        # https://cat.csiss.gmu.edu/CropSmart#map=5.16/-95.11/38.26
        
        return tools.msg()
    except Exception as e:
        return tools.msg_err(e)