from flask import Blueprint, render_template, redirect, url_for
from utils.conexion import main_variables_col, field_data_col
import json
import re
import os
from utils import tools
from utils.ai.tools import save_page_screenshot
from utils.ai.main import prompt, search_internet

bp = Blueprint("Principal", __name__)


@bp.route("/Principal")
def Principal():
    try:
        # Load main variables from database
        main_data = main_variables_col.find_one({}, {"_id": 0})

        # If no main variables exist, redirect to initial setup
        if not main_data:
            return redirect(url_for("VariablesDeInicio.initial_variables"))

        # Load field data if available
        field_data = field_data_col.find_one({}, {"_id": 0})

        # Clean up timestamps
        if main_data and "updated_at" in main_data:
            del main_data["updated_at"]
        if field_data and "updated_at" in field_data:
            del field_data["updated_at"]

        return render_template(
            "Principal.html", main_data=main_data or {}, field_data=field_data or {}
        )
    except Exception as e:
        print(f"Error loading data: {e}")
        return render_template("Principal.html", main_data={}, field_data={})


@bp.route("/Calculate", methods=["POST"])
def Calculate():
    try:
        # Load data from database instead of request
        main_data = main_variables_col.find_one({}, {"_id": 0})
        if not main_data:
            return tools.msg(
                1, "No main variables found. Please configure initial data first."
            )

        field_data = field_data_col.find_one({}, {"_id": 0}) or {}

        # Extract main variables
        ancho: float = float(main_data["width"])
        alto: float = float(main_data["length"])
        tipo_planta: str = main_data["plant_type"]
        lat: float = main_data["latitude"]
        lng: float = main_data["longitude"]

        url = f"https://cat.csiss.gmu.edu/CropSmart#map=7.4/{lng}/{lat}"
        path = f"static/imgs/data/m_{lat}_{lng}.png"

        # Check if screenshot already exists
        if os.path.exists(path):
            mapa = path
        else:
            mapa = save_page_screenshot(url, path)

        # Do searches directly (faster than function calling)

        busqueda_temperatura = search_internet(
            query=f"Soil temperature in the following location: Latitude: {lat}, Longitude: {lng}"
        )

        busqueda_demanda = search_internet(
            query=f"Market demand for the following crop: {tipo_planta}"
        )

        busqueda_clima = search_internet(
            query=f"Weather forecast in the following location: Latitude: {lat}, Longitude: {lng}"
        )

        # Prepare field data section
        field_data_text = ""
        if field_data:
            field_data_text = f"""
**Field measurements:**
- Water pH: {field_data.get("water_ph", "Not measured")}
- Water Conductivity: {field_data.get("water_conductivity", "Not measured")}
- Soil Salinity: {field_data.get("soil_salinity", "Not measured")}
- Soil Moisture: {field_data.get("soil_moisture", "Not measured")}
"""

        ai_response = prompt(
            prompt_param=f"""
Analyze the following data from an agricultural field and the attached satellite map:
- Width: {ancho} meters
- Length: {alto} meters  
- Total area: {ancho * alto} m²
- Plant type: {tipo_planta}
- Location: Latitude {lat}, Longitude {lng}
{field_data_text}
**Information from internet searches:**

Soil temperature:
{json.dumps(busqueda_temperatura, indent=2, ensure_ascii=False)}

Market demand:
{json.dumps(busqueda_demanda, indent=2, ensure_ascii=False)}

Weather forecast:
{json.dumps(busqueda_clima, indent=2, ensure_ascii=False)}

Based on this information, generate a JSON with the requested data.
            """,
            files=[mapa],
            system_prompt="""
You are an agriculture expert. Analyze the provided information and respond ONLY with a valid JSON:

{
    "temperatura_suelo": "<value in °C or estimate based on info>",
    "demanda_producto": "<High/Medium/Low with brief context>",
    "probabilidad_lluvia": "<percentage or level>"
}

RULES:
- Only return the JSON, nothing else
- If info is missing, estimate based on context
- Be concise
            """,
        )

        # Parse Gemini's JSON response
        try:
            # Extract JSON from response (may come with markdown ```json```)
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                datos_calculados = json.loads(json_match.group())
            else:
                datos_calculados = {
                    "temperatura_suelo": "Not available",
                    "demanda_producto": "Not available",
                    "probabilidad_lluvia": "Not available",
                }
        except json.JSONDecodeError:
            datos_calculados = {
                "temperatura_suelo": "Processing error",
                "demanda_producto": "Processing error",
                "probabilidad_lluvia": "Processing error",
            }

        return tools.msg(
            url_mapa=mapa,
            temperatura_suelo=datos_calculados.get(
                "temperatura_suelo", "Not available"
            ),
            demanda_producto=datos_calculados.get("demanda_producto", "Not available"),
            probabilidad_lluvia=datos_calculados.get(
                "probabilidad_lluvia", "Not available"
            ),
        )
    except Exception as e:
        return tools.msg_err(e)
