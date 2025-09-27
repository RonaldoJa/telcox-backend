from flask import request, jsonify
from flask_restful import Resource
from app.models.customer import Customer, Consumption
from app.services.bss_simulator import BSSSimulator
from app import db
import logging

logger = logging.getLogger(__name__)


class CustomerInfoAPI(Resource):
    """API para información básica del cliente"""

    def get(self, customer_id):
        """
        Obtener información básica del cliente

        Args:
            customer_id (int): ID del cliente

        Returns:
            dict: Información del cliente o error
        """
        try:
            customer = Customer.query.get(customer_id)

            if not customer:
                logger.warning(f"Customer {customer_id} not found")
                return {'error': 'Cliente no encontrado'}, 404

            logger.info(f"Customer info retrieved for customer {customer_id}")
            return {
                'success': True,
                'data': customer.to_dict()
            }, 200

        except Exception as e:
            logger.error(f"Error retrieving customer info for {customer_id}: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500


class CustomerConsumptionAPI(Resource):
    """API para datos de consumo del cliente"""

    def __init__(self):
        self.bss_simulator = BSSSimulator()

    def get(self, customer_id):
        """
        Obtener datos de consumo del cliente en tiempo real

        Args:
            customer_id (int): ID del cliente

        Returns:
            dict: Datos de consumo en tiempo real o error
        """
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                logger.warning(f"Customer {customer_id} not found for consumption request")
                return {'error': 'Cliente no encontrado'}, 404

            bss_data = self.bss_simulator.get_customer_consumption(customer_id)
            if not bss_data:
                logger.error(f"BSS data unavailable for customer {customer_id}")
                return {
                    'error': 'Sistema BSS temporalmente no disponible. Intente nuevamente.'
                }, 503

            consumption = Consumption.query.filter_by(customer_id=customer_id).first()
            if not consumption:
                logger.error(f"Consumption data not initialized for customer {customer_id}")
                return {'error': 'Datos de consumo no inicializados para este cliente'}, 404

            self._update_consumption_from_bss(consumption, bss_data)

            response_data = {
                'customer': customer.to_dict(),
                'consumption': consumption.to_dict(),
                'real_time_data': {
                    'bss_status': bss_data.get('bss_status', 'unknown'),
                    'last_sync': bss_data.get('last_sync'),
                    'sync_quality': bss_data.get('sync_quality', 'medium'),
                    'response_time_ms': bss_data.get('response_time_ms', 0)
                }
            }

            logger.info(f"Consumption data retrieved successfully for customer {customer_id}")
            return {'success': True, 'data': response_data}, 200

        except Exception as e:
            logger.error(f"Error retrieving consumption for customer {customer_id}: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    def _update_consumption_from_bss(self, consumption, bss_data):
        """
        Actualizar datos de consumo con información del BSS

        Args:
            consumption (Consumption): Objeto de consumo a actualizar
            bss_data (dict): Datos del sistema BSS
        """
        try:
            if 'data_used_mb' in bss_data:
                consumption.data_used_mb = max(0, bss_data['data_used_mb'])

            if 'minutes_used' in bss_data:
                consumption.minutes_used = max(0, bss_data['minutes_used'])

            if 'account_balance' in bss_data:
                consumption.account_balance = max(0, bss_data['account_balance'])

            db.session.commit()

        except Exception as e:
            logger.error(f"Error updating consumption from BSS data: {e}")
            db.session.rollback()
            raise


class BSSystemStatusAPI(Resource):
    """API para verificar el estado del sistema BSS"""

    def __init__(self):
        self.bss_simulator = BSSSimulator()

    def get(self):
        """Obtener estado actual del sistema BSS"""
        try:
            status = self.bss_simulator.check_bss_status()
            return {'success': True, 'data': status}, 200

        except Exception as e:
            logger.error(f"Error checking BSS status: {e}")
            return {'error': 'Error verificando estado del sistema'}, 500