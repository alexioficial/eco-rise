from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

from routes.Inicio import bp as Inicio
from routes.Principal import bp as Principal
from routes.VariablesDeInicio import bp as VariablesDeInicio
from routes.DatosDeCampo import bp as DatosDeCampo

app.register_blueprint(Inicio)
app.register_blueprint(Principal)
app.register_blueprint(VariablesDeInicio)
app.register_blueprint(DatosDeCampo)

if __name__ == '__main__':
    app.run(debug=True, port=7100)
