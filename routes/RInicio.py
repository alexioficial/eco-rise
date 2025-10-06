from flask import Blueprint, redirect, request, make_response

bp = Blueprint("Inicio", __name__)

@bp.route("/")
def Inicio():
    if request.cookies.get("demo_mode") == "1":
        return redirect("/VariablesDeInicio")
    # If demo mode is explicitly requested via query string, set cookie and allow entry
    if request.args.get("demo_mode") == "1":
        resp = make_response(redirect("/VariablesDeInicio"))
        # Cookie must be readable by JS (HttpOnly=False) because base.html will validate it on the client
        resp.set_cookie(
            key="demo_mode",
            value="1",
            max_age=60 * 24 * 60 * 60,  # 60 days
            path="/",
            samesite="Lax",
            secure=False,  # set True if you always serve over HTTPS
            httponly=False,
        )
        return resp

    # Otherwise, redirect to public site
    return redirect("https://eco-rise.surge.sh")
