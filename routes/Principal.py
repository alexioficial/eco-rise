from flask import Blueprint, render_template, request
import json
import re
import os
from utils import tools
from utils.ai.tools import save_page_screenshot
from utils.ai.main import prompt, search_internet

bp = Blueprint("Principal", __name__)


@bp.route("/Principal")
def Principal():
    return render_template("Principal.html")


@bp.route("/Calculate", methods=["POST"])
def Calculate():
    try:
        data = request.get_json()

        _ancho: float = float(data["ancho"])
        _alto: float = float(data["alto"])
        _tipo_planta: str = data["tipo_planta"]
        lat: str = data["lat"]
        lng: str = data["lng"]

        url = f"https://cat.csiss.gmu.edu/CropSmart#map=7.4/{lng}/{lat}"
        path = f"static/imgs/data/m_{lat}_{lng}.png"

        # Verificar si el screenshot ya existe
        if os.path.exists(path):
            mapa = path
        else:
            mapa = save_page_screenshot(url, path)

        # Hacer búsquedas directamente (más rápido que function calling)

        busqueda_temperatura = search_internet(
            f"temperatura suelo {_tipo_planta} {lat} {lng}", max_results=2
        )
        busqueda_demanda = search_internet(
            f"demanda mercado {_tipo_planta} Estados Unidos", max_results=2
        )
        busqueda_clima = search_internet(f"pronóstico clima {lat} {lng}", max_results=2)

        ai_response = prompt(
            prompt_param=f"""
Analiza los siguientes datos de un terreno agrícola y el mapa satelital adjunto:

**Datos del terreno:**
- Ancho: {_ancho} metros
- Alto: {_alto} metros  
- Área total: {_ancho * _alto} m²
- Tipo de planta: {_tipo_planta}
- Ubicación: {lat}, {lng}

**Información de búsquedas en internet:**

Temperatura del suelo:
{json.dumps(busqueda_temperatura, indent=2, ensure_ascii=False)}

Demanda de mercado:
{json.dumps(busqueda_demanda, indent=2, ensure_ascii=False)}

Pronóstico climático:
{json.dumps(busqueda_clima, indent=2, ensure_ascii=False)}

Basándote en esta información, genera un JSON con los datos solicitados.
            """,
            files=[mapa],
            system_prompt="""
Eres un experto en agricultura. Analiza la información proporcionada y responde ÚNICAMENTE con un JSON válido:

{
    "temperatura_suelo": "<valor en °C o estimación basada en la info>",
    "demanda_producto": "<Alta/Media/Baja con breve contexto>",
    "probabilidad_lluvia": "<porcentaje o nivel>"
}

REGLAS:
- Solo retorna el JSON, nada más
- Si falta info, estima basándote en el contexto
- Sé conciso
            """,
        )

        # Parsear la respuesta JSON de Gemini
        try:
            # Extraer JSON de la respuesta (puede venir con markdown ```json```)
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                datos_calculados = json.loads(json_match.group())
            else:
                datos_calculados = {
                    "temperatura_suelo": "No disponible",
                    "demanda_producto": "No disponible",
                    "probabilidad_lluvia": "No disponible",
                }
        except json.JSONDecodeError:
            datos_calculados = {
                "temperatura_suelo": "Error al procesar",
                "demanda_producto": "Error al procesar",
                "probabilidad_lluvia": "Error al procesar",
            }

        return tools.msg(
            url_mapa=mapa,
            temperatura_suelo=datos_calculados.get(
                "temperatura_suelo", "No disponible"
            ),
            demanda_producto=datos_calculados.get("demanda_producto", "No disponible"),
            probabilidad_lluvia=datos_calculados.get(
                "probabilidad_lluvia", "No disponible"
            ),
        )
    except Exception as e:
        return tools.msg_err(e)
