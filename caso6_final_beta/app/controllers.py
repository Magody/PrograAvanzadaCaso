from flask import Blueprint, request, render_template
from .models import DataLoader

bp = Blueprint('main', __name__)

data_loader = DataLoader()
data_loader.load_data()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/search')
def search():
    id_pedido = request.args.get('id_pedido')
    pedido_info = next((pedido for pedido in data_loader.pedidos if pedido.id_pedido == id_pedido), None)
    
    if pedido_info:
        cliente_info = next((cliente for cliente in data_loader.clientes if cliente.id_cliente == pedido_info.id_cliente), None)
        plato_info = next((plato for plato in data_loader.menu if plato.codigo_plato == pedido_info.codigo_plato), None)
        
        return render_template('results.html', pedido=pedido_info, cliente=cliente_info, plato=plato_info)
    else:
        return "Pedido no encontrado", 404
