from flask import Blueprint, render_template, request
from utils import tools
from utils.conexion import main_variables_col
from datetime import datetime

bp = Blueprint("VariablesDeInicio", __name__)


@bp.route("/VariablesDeInicio")
def initial_variables():
    try:
        # Load existing data from database
        data = main_variables_col.find_one({}, {"_id": 0})
        
        if data and "updated_at" in data:
            del data["updated_at"]
        
        return render_template("VariablesDeInicio.html", main_data=data or {})
    except Exception as e:
        print(f"Error loading main variables: {e}")
        return render_template("VariablesDeInicio.html", main_data={})


@bp.route("/SaveMainVariables", methods=["POST"])
def save_main_variables():
    try:
        data: dict = request.get_json()

        # Validate required fields
        required_fields = ["width", "length", "plant_type", "lat", "lng"]
        for field in required_fields:
            if field not in data:
                return tools.msg(1, f"Missing required field: {field}")

        # Prepare document to save
        doc = {
            "width": float(data["width"]),
            "length": float(data["length"]),
            "plant_type": data["plant_type"],
            "latitude": float(data["lat"]),
            "longitude": float(data["lng"]),
            "updated_at": datetime.now(),
        }

        # Update or insert (only one document should exist)
        main_variables_col.update_one(
            {},  # Empty filter matches the first/only document
            {"$set": doc},
            upsert=True,
        )

        return tools.msg(0, "Main variables saved successfully")
    except Exception as e:
        return tools.msg_err(e)


@bp.route("/GetMainVariables", methods=["GET"])
def get_main_variables():
    try:
        # Get the single document from the collection
        data = main_variables_col.find_one({}, {"_id": 0})

        if data:
            # Remove updated_at from response for cleaner data
            if "updated_at" in data:
                del data["updated_at"]
            return tools.msg(0, "Data retrieved successfully", data=data)
        else:
            return tools.msg(0, "No data found", data=None)
    except Exception as e:
        return tools.msg_err(e)
