from flask import Flask
from routes.RInicio import bp as Inicio
from routes.Principal import bp as Principal
from routes.VariablesDeInicio import bp as VariablesDeInicio
from routes.DatosDeCampo import bp as DatosDeCampo

app = Flask(__name__)

app.register_blueprint(Inicio)
app.register_blueprint(Principal)
app.register_blueprint(VariablesDeInicio)
app.register_blueprint(DatosDeCampo)

if __name__ == "__main__":
    app.run(debug=True, port=7100)
