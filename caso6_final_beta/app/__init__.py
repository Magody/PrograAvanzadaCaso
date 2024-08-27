from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # Configura la aplicación aquí, por ejemplo:
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    # Importa y registra los blueprints
    from .controllers import bp
    app.register_blueprint(bp)
    
    # Otras configuraciones o inicializaciones necesarias
    
    return app
