from flask import Blueprint, render_template, request
from utils import tools
from utils.conexion import field_data_col
from datetime import datetime

bp = Blueprint("DatosDeCampo", __name__)


@bp.route("/DatosDeCampo")
def field_data():
    try:
        # Load existing data from database
        data = field_data_col.find_one({}, {"_id": 0})
        
        if data and "updated_at" in data:
            del data["updated_at"]
        
        return render_template("DatosDeCampo.html", field_data=data or {})
    except Exception as e:
        print(f"Error loading field data: {e}")
        return render_template("DatosDeCampo.html", field_data={})


@bp.route("/SaveFieldData", methods=["POST"])
def save_field_data():
    try:
        data: dict = request.get_json()

        doc = {
            "water_ph": float(data.get("water_ph", 0))
            if data.get("water_ph")
            else None,
            "water_conductivity": float(data.get("water_conductivity", 0))
            if data.get("water_conductivity")
            else None,
            "soil_salinity": float(data.get("soil_salinity", 0))
            if data.get("soil_salinity")
            else None,
            "soil_moisture": float(data.get("soil_moisture", 0))
            if data.get("soil_moisture")
            else None,
            "updated_at": datetime.now(),
        }

        field_data_col.update_one({}, {"$set": doc}, upsert=True)

        return tools.msg(0, "Field data saved successfully")
    except Exception as e:
        return tools.msg_err(e)


@bp.route("/GetFieldData", methods=["GET"])
def get_field_data():
    try:
        data = field_data_col.find_one({}, {"_id": 0})

        if data:
            # Remove updated_at from response for cleaner data
            if "updated_at" in data:
                del data["updated_at"]
            return tools.msg(0, "Data retrieved successfully", data=data)
        else:
            return tools.msg(0, "No data found", data=None)
    except Exception as e:
        return tools.msg_err(e)
