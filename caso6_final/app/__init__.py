from flask import Flask
from .controllers import bp as main_bp
import os

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    
    # Configura la aplicación si es necesario
    app.config['SECRET_KEY'] = 'mi_clave_secreta'  # Ejemplo de configuración
    
    # Registra los blueprints
    app.register_blueprint(main_bp)
    
    return app
