from flask import Blueprint, render_template, redirect, url_for
from utils.conexion import main_variables_col, field_data_col, calculated_data_col
import json
import re
import os
import hashlib
from utils import tools
from utils.ai.tools import save_page_screenshot
from utils.ai.main import prompt, search_internet
from datetime import datetime

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

        # Create unique cache key based on all input parameters
        cache_key_data = {
            "width": main_data.get("width"),
            "length": main_data.get("length"),
            "plant_type": main_data.get("plant_type"),
            "latitude": main_data.get("latitude"),
            "longitude": main_data.get("longitude"),
            "water_ph": field_data.get("water_ph"),
            "water_conductivity": field_data.get("water_conductivity"),
            "soil_salinity": field_data.get("soil_salinity"),
            "soil_moisture": field_data.get("soil_moisture"),
        }
        cache_key = hashlib.md5(
            json.dumps(cache_key_data, sort_keys=True).encode()
        ).hexdigest()

        # Check if we have cached data for these parameters
        cached_result = calculated_data_col.find_one({"cache_key": cache_key})
        if cached_result:
            print(f"Cache HIT for key: {cache_key}")
            return tools.msg(
                0,
                "Data retrieved from cache",
                url_mapa=cached_result.get("url_mapa"),
                temperatura_suelo=cached_result.get("temperatura_suelo"),
                demanda_producto=cached_result.get("demanda_producto"),
                probabilidad_lluvia=cached_result.get("probabilidad_lluvia"),
                efectividad_cultivo=cached_result.get("efectividad_cultivo"),
                from_cache=True,
            )

        print(f"Cache MISS for key: {cache_key}. Calculating...")

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
    "temperatura_suelo": "<numeric value in °F (Fahrenheit)>",
    "demanda_producto": "<ONLY one word: High, Medium, or Low>",
    "probabilidad_lluvia": "<numeric percentage value without % symbol, e.g., 20, 45, 80>",
    "efectividad_cultivo": "<numeric percentage (0-100) representing crop effectiveness based on all conditions>"
}

RULES:
- Only return the JSON, nothing else
- temperatura_suelo must be in Fahrenheit (°F)
- demanda_producto must be EXACTLY one of these words: High, Medium, Low (no additional text)
- probabilidad_lluvia must be a number only (e.g., 20, not "20%")
- efectividad_cultivo should consider soil conditions, plant type, location, field measurements, and climate
- If info is missing, make a reasonable estimate based on available context
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
                    "demanda_producto": "Medium",
                    "probabilidad_lluvia": "Not available",
                    "efectividad_cultivo": "Not available",
                }
        except json.JSONDecodeError:
            datos_calculados = {
                "temperatura_suelo": "Processing error",
                "demanda_producto": "Medium",
                "probabilidad_lluvia": "Processing error",
                "efectividad_cultivo": "Processing error",
            }

        # Prepare response data
        response_data = {
            "url_mapa": mapa,
            "temperatura_suelo": datos_calculados.get(
                "temperatura_suelo", "Not available"
            ),
            "demanda_producto": datos_calculados.get("demanda_producto", "Medium"),
            "probabilidad_lluvia": datos_calculados.get(
                "probabilidad_lluvia", "Not available"
            ),
            "efectividad_cultivo": datos_calculados.get(
                "efectividad_cultivo", "Not available"
            ),
        }

        # Save to cache collection
        cache_document = {
            "cache_key": cache_key,
            "input_params": cache_key_data,
            "calculated_at": datetime.now(),
            **response_data,
        }
        calculated_data_col.update_one(
            {"cache_key": cache_key}, {"$set": cache_document}, upsert=True
        )
        print(f"Saved calculation to cache with key: {cache_key}")

        return tools.msg(0, "Data calculated successfully", **response_data)
    except Exception as e:
        return tools.msg_err(e)


@bp.route("/GetAdvice", methods=["POST"])
def GetAdvice():
    try:
        # Load data from database
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

        # Get the map screenshot path
        path = f"static/imgs/data/m_{lat}_{lng}.png"
        if not os.path.exists(path):
            return tools.msg(
                1,
                "Map screenshot not found. Please calculate data first by loading the main page.",
            )

        # Prepare field data text
        field_measurements = []
        if field_data.get("water_ph"):
            field_measurements.append(f"Water pH: {field_data['water_ph']}")
        if field_data.get("water_conductivity"):
            field_measurements.append(
                f"Water Conductivity: {field_data['water_conductivity']}"
            )
        if field_data.get("soil_salinity"):
            field_measurements.append(f"Soil Salinity: {field_data['soil_salinity']}")
        if field_data.get("soil_moisture"):
            field_measurements.append(f"Soil Moisture: {field_data['soil_moisture']}%")

        field_data_text = (
            "\n".join(field_measurements)
            if field_measurements
            else "No field measurements available"
        )

        # Get the cached calculation results if available
        cache_key_data = {
            "width": main_data.get("width"),
            "length": main_data.get("length"),
            "plant_type": main_data.get("plant_type"),
            "latitude": main_data.get("latitude"),
            "longitude": main_data.get("longitude"),
            "water_ph": field_data.get("water_ph"),
            "water_conductivity": field_data.get("water_conductivity"),
            "soil_salinity": field_data.get("soil_salinity"),
            "soil_moisture": field_data.get("soil_moisture"),
        }
        cache_key = hashlib.md5(
            json.dumps(cache_key_data, sort_keys=True).encode()
        ).hexdigest()

        cached_result = calculated_data_col.find_one({"cache_key": cache_key})
        
        # Check if advice already exists in cache
        if cached_result and cached_result.get("advice"):
            print(f"Advice Cache HIT for key: {cache_key}")
            return tools.msg(
                0, "Advice retrieved from cache", advice=cached_result["advice"]
            )
        
        print(f"Advice Cache MISS for key: {cache_key}. Generating advice...")
        
        if cached_result:
            temperatura_suelo = cached_result.get("temperatura_suelo", "Not available")
            demanda_producto = cached_result.get("demanda_producto", "Unknown")
            probabilidad_lluvia = cached_result.get(
                "probabilidad_lluvia", "Not available"
            )
            efectividad_cultivo = cached_result.get(
                "efectividad_cultivo", "Not available"
            )
        else:
            # If no cached data, provide generic values
            temperatura_suelo = "Not calculated"
            demanda_producto = "Unknown"
            probabilidad_lluvia = "Not calculated"
            efectividad_cultivo = "Not calculated"

        # Generate AI advice
        ai_response = prompt(
            prompt_param=f"""
You are an expert agricultural consultant. Based on the following farm data, provide a detailed yet concise recommendation on how to improve crop effectiveness.

**Farm Information:**
- Dimensions: {ancho}m x {alto}m (Total: {ancho * alto}m²)
- Plant Type: {tipo_planta}
- Location: Latitude {lat}, Longitude {lng}

**Field Measurements:**
{field_data_text}

**Calculated Metrics:**
- Soil Temperature: {temperatura_suelo}°F
- Product Market Demand: {demanda_producto}
- Rain Probability: {probabilidad_lluvia}%
- Current Crop Effectiveness: {efectividad_cultivo}%

Provide practical advice on how to improve the crop effectiveness percentage. Explain why the current effectiveness is at this level and what specific actions can be taken to improve it.

MAXIMUM 150 WORDS. Be specific and actionable.
            """,
            files=[path],
            system_prompt="""
You are an agricultural expert providing actionable advice to farmers.

RULES:
- Maximum 150 words
- Be specific and practical
- Focus on concrete actions
- Explain why effectiveness is at current level
- Suggest 2-3 specific improvements
- Use clear, simple language
- No bullet points, write in paragraph form
- Be encouraging but realistic
            """,
        )

        # Clean up the response (remove any markdown or extra formatting)
        advice = ai_response.strip()

        # Save advice to cache
        calculated_data_col.update_one(
            {"cache_key": cache_key},
            {"$set": {"advice": advice, "advice_generated_at": datetime.now()}},
            upsert=True,
        )
        print(f"Saved advice to cache with key: {cache_key}")

        return tools.msg(0, "Advice generated successfully", advice=advice)
    except Exception as e:
        return tools.msg_err(e)
