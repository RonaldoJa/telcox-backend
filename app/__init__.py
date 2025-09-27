# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Crear instancia de SQLAlchemy
db = SQLAlchemy()


def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)

    # Configuración de la aplicación
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "telcox.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'telcox-dev-secret-key'

    # Inicializar extensiones
    db.init_app(app)
    CORS(app, origins=['http://localhost:4200', 'http://127.0.0.1:4200'])

    # Registrar blueprints/APIs dentro del contexto de la app
    with app.app_context():
        register_apis(app)

    return app


def register_apis(app):
    """Registrar todas las APIs"""
    from flask_restful import Api

    # Crear API
    api = Api(app)

    # Importar APIs
    from app.apis.customer_api import (
        CustomerInfoAPI,
        CustomerConsumptionAPI,
        NetworkMetricsAPI,
        UsageHistoryAPI,
        BillingCycleAPI,
        CustomersListAPI,
        BSSystemStatusAPI
    )

    # Registrar rutas
    api.add_resource(BSSystemStatusAPI, '/api/system-status')
    api.add_resource(CustomerInfoAPI, '/api/customers/<int:customer_id>')
    api.add_resource(CustomersListAPI, '/api/customers')
    api.add_resource(CustomerConsumptionAPI, '/api/customers/<int:customer_id>/consumption')
    api.add_resource(NetworkMetricsAPI, '/api/customers/<int:customer_id>/network-metrics')
    api.add_resource(UsageHistoryAPI, '/api/customers/<int:customer_id>/usage-history')
    api.add_resource(BillingCycleAPI, '/api/customers/<int:customer_id>/billing-cycle')