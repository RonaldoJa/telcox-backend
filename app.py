# app.py - Archivo principal
from flask import jsonify
from datetime import datetime
import logging
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_complete_app():
    """Crear aplicación completa con todas las configuraciones"""

    # Importar el factory function
    from app import create_app, db

    # Crear la aplicación
    app = create_app()

    # Agregar rutas adicionales
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'telcox-backend',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        })

    @app.route('/api/info')
    def api_info():
        """Información de la API y endpoints disponibles"""
        return jsonify({
            'name': 'Telcox Backend API',
            'version': '1.0.0',
            'description': 'API para el sistema de gestión de clientes Telcox',
            'endpoints': {
                'system': [
                    'GET /api/health - Health check',
                    'GET /api/system-status - Estado del sistema BSS',
                    'GET /api/info - Información de la API'
                ],
                'customers': [
                    'GET /api/customers - Lista de clientes (con paginación)',
                    'GET /api/customers/<id> - Información del cliente',
                    'GET /api/customers/<id>/consumption - Datos de consumo',
                    'GET /api/customers/<id>/network-metrics - Métricas de red',
                    'GET /api/customers/<id>/usage-history - Historial de uso',
                    'GET /api/customers/<id>/billing-cycle - Ciclo de facturación'
                ]
            }
        })

    @app.route('/debug/routes')
    def debug_routes():
        """Listar todas las rutas registradas"""
        routes = []
        for rule in app.url_map.iter_rules():
            methods = list(rule.methods - {'HEAD', 'OPTIONS'})
            routes.append({
                'endpoint': rule.endpoint,
                'methods': methods,
                'rule': rule.rule
            })

        return jsonify({
            'total_routes': len(routes),
            'routes': routes
        })

    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint no encontrado',
            'message': 'La ruta solicitada no existe',
            'available_info': '/api/info'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ha ocurrido un error inesperado',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

    return app, db


def initialize_database(app, db):
    """Inicializar base de datos y datos de prueba"""
    with app.app_context():
        try:
            logger.info("Inicializando base de datos...")

            # Crear tablas si no existen
            db.create_all()
            logger.info("Tablas creadas correctamente")

            # Verificar si ya hay datos
            from app.models.customer import Customer
            if Customer.query.count() == 0:
                logger.info("Cargando datos de prueba...")
                create_test_data(db)
                logger.info("Datos de prueba cargados")
            else:
                logger.info("Datos ya existen, omitiendo seed")

        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise


def create_test_data(db):
    """Crear datos de prueba básicos"""
    from app.models.customer import Customer, Consumption
    from datetime import date, timedelta

    # Datos de clientes
    customers_data = [
        {
            'name': 'Juan Carlos Pérez',
            'email': 'juan.perez@email.com',
            'phone': '+593 987 654 321',
            'plan_type': 'Premium'
        },
        {
            'name': 'María Elena González',
            'email': 'maria.gonzalez@email.com',
            'phone': '+593 976 543 210',
            'plan_type': 'Básico'
        },
        {
            'name': 'Carlos Roberto Rodríguez',
            'email': 'carlos.rodriguez@email.com',
            'phone': '+593 965 432 109',
            'plan_type': 'Empresarial'
        },
        {
            'name': 'Ana Sofía Mendoza',
            'email': 'ana.mendoza@email.com',
            'phone': '+593 954 321 098',
            'plan_type': 'Familiar'
        }
    ]

    # Crear clientes y consumo
    for i, customer_data in enumerate(customers_data, 1):
        customer = Customer(**customer_data)
        db.session.add(customer)
        db.session.flush()  # Para obtener el ID

        # Crear datos de consumo
        today = date.today()
        cycle_start = today.replace(day=1)

        # Calcular fecha de fin de ciclo
        if cycle_start.month == 12:
            cycle_end = cycle_start.replace(year=cycle_start.year + 1, month=1) - timedelta(days=1)
        else:
            cycle_end = cycle_start.replace(month=cycle_start.month + 1) - timedelta(days=1)

        # Límites según el plan
        plan_limits = {
            'Básico': {'data': 2048, 'minutes': 300},
            'Premium': {'data': 5120, 'minutes': 500},
            'Empresarial': {'data': 10240, 'minutes': 1000},
            'Familiar': {'data': 7168, 'minutes': 750}
        }

        limits = plan_limits.get(customer.plan_type, {'data': 5120, 'minutes': 500})

        consumption = Consumption(
            customer_id=customer.id,
            data_used_mb=round(limits['data'] * 0.6 + (i * 200), 2),
            data_limit_mb=limits['data'],
            minutes_used=int(limits['minutes'] * 0.4 + (i * 50)),
            minutes_limit=limits['minutes'],
            account_balance=round(25.50 + (i * 8.25), 2),
            billing_cycle_start=cycle_start,
            billing_cycle_end=cycle_end
        )

        db.session.add(consumption)

    db.session.commit()
    logger.info(f"Creados {len(customers_data)} clientes con datos de consumo")


if __name__ == '__main__':
    # Crear aplicación
    app, db = create_complete_app()

    # Inicializar base de datos
    initialize_database(app, db)

    # Mostrar rutas registradas
    with app.app_context():
        print("\n" + "=" * 60)
        print("🚀 TELCOX BACKEND API - RUTAS REGISTRADAS")
        print("=" * 60)

        for rule in app.url_map.iter_rules():
            methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"{methods:15} {rule.rule}")

        print("=" * 60)
        print(f"📍 Servidor iniciando en: http://127.0.0.1:5100")
        print(f"📋 Información de API: http://127.0.0.1:5100/api/info")
        print(f"💚 Health check: http://127.0.0.1:5100/api/health")
        print(f"🔍 Debug rutas: http://127.0.0.1:5100/debug/routes")
        print("=" * 60)

    # Ejecutar servidor
    app.run(
        host='127.0.0.1',
        port=5100,
        debug=True,
        threaded=True
    )