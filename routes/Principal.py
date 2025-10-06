from flask import Blueprint, render_template
# from flask import request
# import json
# import re
# import os
# from utils import tools
# from utils.ai.tools import save_page_screenshot
# from utils.ai.main import prompt, search_internet

bp = Blueprint("Principal", __name__)


@bp.route("/Principal")
def Principal():
    return render_template("Principal.html")


# @bp.route("/Calculate", methods=["POST"])
# def Calculate():
#     try:
#         data = request.get_json()

#         _ancho: float = float(data["ancho"])
#         _alto: float = float(data["alto"])
#         _tipo_planta: str = data["tipo_planta"]
#         lat: str = data["lat"]
#         lng: str = data["lng"]

#         url = f"https://cat.csiss.gmu.edu/CropSmart#map=7.4/{lng}/{lat}"
#         path = f"static/imgs/data/m_{lat}_{lng}.png"

#         # Check if screenshot already exists
#         if os.path.exists(path):
#             mapa = path
#         else:
#             mapa = save_page_screenshot(url, path)

#         # Do searches directly (faster than function calling)

#         )

#         ai_response = prompt(
#             prompt_param=f"""
# Analyze the following data from an agricultural field and the attached satellite map:
# - Width: {_ancho} meters
# - Height: {_alto} meters  
# - Total area: {_ancho * _alto} m²
# - Plant type: {_tipo_planta}
# - Location: {lat}, {lng}

# **Information from internet searches:**

# Soil temperature:
# {json.dumps(busqueda_temperatura, indent=2, ensure_ascii=False)}

# Market demand:
# {json.dumps(busqueda_demanda, indent=2, ensure_ascii=False)}

# Weather forecast:
# {json.dumps(busqueda_clima, indent=2, ensure_ascii=False)}

# Based on this information, generate a JSON with the requested data.
#             """,
#             files=[mapa],
#             system_prompt="""
# You are an agriculture expert. Analyze the provided information and respond ONLY with a valid JSON:

# {
#     "temperatura_suelo": "<value in °C or estimate based on info>",
#     "demanda_producto": "<High/Medium/Low with brief context>",
#     "probabilidad_lluvia": "<percentage or level>"
# }

# RULES:
# - Only return the JSON, nothing else
# - If info is missing, estimate based on context
# - Be concise
#             """,
#         )

#         # Parse Gemini's JSON response
#         try:
#             # Extract JSON from response (may come with markdown ```json```)
#             json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
#             if json_match:
#                 datos_calculados = json.loads(json_match.group())
#             else:
#                 datos_calculados = {
#                     "temperatura_suelo": "Not available",
#                     "demanda_producto": "Not available",
#                     "probabilidad_lluvia": "Not available",
#                 }
#         except json.JSONDecodeError:
#             datos_calculados = {
#                 "temperatura_suelo": "Processing error",
#                 "demanda_producto": "Processing error",
#                 "probabilidad_lluvia": "Processing error",
#             }

#         return tools.msg(
#             url_mapa=mapa,
#             temperatura_suelo=datos_calculados.get(
#                 "temperatura_suelo", "Not available"
#             ),
#             demanda_producto=datos_calculados.get("demanda_producto", "Not available"),
#             probabilidad_lluvia=datos_calculados.get(
#                 "probabilidad_lluvia", "Not available"
#             ),
#         )
#     except Exception as e:
#         return tools.msg_err(e)
