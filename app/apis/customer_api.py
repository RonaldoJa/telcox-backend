from flask import request, jsonify
from flask_restful import Resource
from app.models.customer import Customer, Consumption
from app.services.bss_simulator import BSSSimulator
from app import db
from datetime import datetime, timedelta, date
import logging
import random

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


class NetworkMetricsAPI(Resource):
    """API para métricas de red (compatible con CustomerService.getNetworkMetrics)"""

    def __init__(self):
        self.bss_simulator = BSSSimulator()

    def get(self, customer_id):
        """
        Obtener métricas de red del cliente

        Returns:
            dict: Métricas de red en tiempo real
        """
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return {'error': 'Cliente no encontrado'}, 404

            consumption = Consumption.query.filter_by(customer_id=customer_id).first()
            if not consumption:
                return {'error': 'Datos de consumo no encontrados'}, 404

            # Generar métricas de red realistas
            network_metrics = self._generate_network_metrics(customer_id, consumption)

            logger.info(f"Network metrics retrieved for customer {customer_id}")
            return {
                'success': True,
                'data': network_metrics
            }, 200

        except Exception as e:
            logger.error(f"Error retrieving network metrics for {customer_id}: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    def _generate_network_metrics(self, customer_id, consumption):
        """Generar métricas de red realistas"""
        current_hour = datetime.now().hour

        plan_speeds = {
            'Básico': {'down': 50, 'up': 25},
            'Premium': {'down': 100, 'up': 50},
            'Empresarial': {'down': 200, 'up': 100},
            'Familiar': {'down': 150, 'up': 75}
        }

        plan_type = consumption.customer.plan_type
        base_speeds = plan_speeds.get(plan_type, {'down': 100, 'up': 50})

        if 18 <= current_hour <= 22:  # Hora pico
            speed_factor = random.uniform(0.7, 0.9)
            latency_factor = random.uniform(1.2, 1.8)
        elif 9 <= current_hour <= 17:  # Horas laborales
            speed_factor = random.uniform(0.85, 0.95)
            latency_factor = random.uniform(1.0, 1.3)
        else:  # Horas valle
            speed_factor = random.uniform(0.95, 1.05)
            latency_factor = random.uniform(0.8, 1.0)

        return {
            'customerId': customer_id,
            'downloadSpeed': round(base_speeds['down'] * speed_factor, 1),
            'uploadSpeed': round(base_speeds['up'] * speed_factor, 1),
            'latency': round(20 * latency_factor, 1),
            'jitter': round(random.uniform(1, 5), 1),
            'packetLoss': round(random.uniform(0, 0.5), 2),
            'signalStrength': random.randint(75, 95),
            'dataUsage': {
                'total': consumption.data_limit_mb,
                'used': consumption.data_used_mb,
                'remaining': consumption.data_remaining_mb,
                'percentage': consumption.data_usage_percentage
            },
            'connectionType': self._get_connection_type(plan_type),
            'lastUpdated': datetime.utcnow().isoformat(),
            'quality': self._assess_connection_quality(base_speeds['down'] * speed_factor, 20 * latency_factor)
        }

    def _get_connection_type(self, plan_type):
        """Determinar tipo de conexión según el plan"""
        connection_types = {
            'Básico': 'ADSL',
            'Premium': 'Fibra Óptica',
            'Empresarial': 'Fibra Dedicada',
            'Familiar': 'Fibra Óptica'
        }
        return connection_types.get(plan_type, 'Fibra Óptica')

    def _assess_connection_quality(self, download_speed, latency):
        """Evaluar calidad de conexión"""
        if download_speed >= 80 and latency <= 25:
            return 'excellent'
        elif download_speed >= 50 and latency <= 40:
            return 'good'
        elif download_speed >= 25 and latency <= 60:
            return 'fair'
        else:
            return 'poor'


class UsageHistoryAPI(Resource):
    """API para historial de uso del cliente"""

    def get(self, customer_id):
        """
        Obtener historial de uso del cliente

        Query params:
        - days: número de días hacia atrás (default: 30)
        """
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return {'error': 'Cliente no encontrado'}, 404

            days = request.args.get('days', 30, type=int)
            days = min(days, 90)  # Limitar a 90 días máximo

            usage_history = self._generate_usage_history(customer_id, days)

            logger.info(f"Usage history retrieved for customer {customer_id} ({days} days)")
            return {
                'success': True,
                'data': usage_history
            }, 200

        except Exception as e:
            logger.error(f"Error getting usage history for customer {customer_id}: {e}")
            return {'error': 'Error interno del servidor'}, 500

    def _generate_usage_history(self, customer_id, days):
        """Generar datos realistas de historial de uso"""
        history = []
        base_date = datetime.now().date()

        consumption = Consumption.query.filter_by(customer_id=customer_id).first()
        daily_avg_data = consumption.data_used_mb / 30 if consumption else 50
        daily_avg_minutes = consumption.minutes_used / 30 if consumption else 5

        for i in range(days):
            date_obj = base_date - timedelta(days=i)

            weekday = date_obj.weekday()
            if weekday >= 5:  
                usage_factor = random.uniform(1.2, 1.8)
            else:  
                usage_factor = random.uniform(0.7, 1.3)

            daily_data = max(10, daily_avg_data * usage_factor * random.uniform(0.5, 1.5))
            daily_minutes = max(1, int(daily_avg_minutes * usage_factor * random.uniform(0.3, 2.0)))

            peak_hours = self._generate_hourly_distribution(daily_data, daily_minutes)

            history.append({
                'date': date_obj.isoformat(),
                'dataUsedMb': round(daily_data, 2),
                'minutesUsed': daily_minutes,
                'sessionsCount': random.randint(5, 25),
                'peakHours': peak_hours,
                'averageSpeed': round(random.uniform(45, 95), 1),
                'qualityScore': round(random.uniform(7.5, 9.8), 1)
            })

        return history

    def _generate_hourly_distribution(self, total_data, total_minutes):
        """Generar distribución de uso por horas del día"""
        peak_hours = []

        high_usage_hours = [8, 9, 12, 13, 18, 19, 20, 21, 22]

        for hour in high_usage_hours:
            if random.random() > 0.3:  # 70% probabilidad de uso en hora pico
                hour_data = random.uniform(0.05, 0.25) * total_data
                hour_minutes = random.randint(0, max(1, int(0.3 * total_minutes)))

                peak_hours.append({
                    'hour': hour,
                    'dataUsedMb': round(hour_data, 2),
                    'minutesUsed': hour_minutes,
                    'averageSpeed': round(random.uniform(30, 80), 1)
                })

        return peak_hours[:5]  

class BillingCycleAPI(Resource):
    """API para información del ciclo de facturación"""

    def get(self, customer_id):
        """Obtener información del ciclo de facturación del cliente"""
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return {'error': 'Cliente no encontrado'}, 404

            consumption = Consumption.query.filter_by(customer_id=customer_id).first()
            if not consumption:
                return {'error': 'Datos de consumo no encontrados'}, 404

            billing_info = self._generate_billing_cycle_info(customer, consumption)

            logger.info(f"Billing cycle info retrieved for customer {customer_id}")
            return {
                'success': True,
                'data': billing_info
            }, 200

        except Exception as e:
            logger.error(f"Error getting billing cycle for customer {customer_id}: {e}")
            return {'error': 'Error interno del servidor'}, 500

    def _generate_billing_cycle_info(self, customer, consumption):
        """Generar información detallada del ciclo de facturación"""

        plan_prices = {
            'Básico': 25.99,
            'Premium': 45.99,
            'Empresarial': 89.99,
            'Familiar': 65.99
        }

        base_price = plan_prices.get(customer.plan_type, 45.99)

        overage_charges = 0
        if consumption.data_usage_percentage > 100:
            excess_mb = consumption.data_used_mb - consumption.data_limit_mb
            overage_charges += (excess_mb / 100) * 2.50  # $2.50 por cada 100MB extra

        if consumption.minutes_usage_percentage > 100:
            excess_minutes = consumption.minutes_used - consumption.minutes_limit
            overage_charges += excess_minutes * 0.15  # $0.15 por minuto extra

        additional_services = random.uniform(0, 8.50)
        taxes = base_price * 0.12  

        total_charges = base_price + overage_charges + additional_services + taxes

        cycle_start = consumption.billing_cycle_start
        cycle_end = consumption.billing_cycle_end
        due_date = cycle_end + timedelta(days=15)

        today = date.today()
        days_remaining = (cycle_end - today).days if cycle_end > today else 0

        return {
            'customerId': customer.id,
            'planType': customer.plan_type,
            'cycleStart': cycle_start.isoformat(),
            'cycleEnd': cycle_end.isoformat(),
            'dueDate': due_date.isoformat(),
            'daysRemaining': max(0, days_remaining),
            'charges': {
                'basePlan': round(base_price, 2),
                'overage': round(overage_charges, 2),
                'additionalServices': round(additional_services, 2),
                'taxes': round(taxes, 2),
                'total': round(total_charges, 2)
            },
            'usage': {
                'dataAllowanceMb': consumption.data_limit_mb,
                'dataUsedMb': consumption.data_used_mb,
                'dataRemainingMb': consumption.data_remaining_mb,
                'dataUsagePercentage': consumption.data_usage_percentage,
                'minutesAllowance': consumption.minutes_limit,
                'minutesUsed': consumption.minutes_used,
                'minutesRemaining': consumption.minutes_remaining,
                'minutesUsagePercentage': consumption.minutes_usage_percentage
            },
            'paymentInfo': {
                'currentBalance': consumption.account_balance,
                'lastPaymentDate': (cycle_start - timedelta(days=2)).isoformat(),
                'lastPaymentAmount': round(random.uniform(35, 95), 2),
                'paymentMethod': 'Tarjeta **** 1234',
                'autoPayEnabled': random.choice([True, False])
            },
            'alerts': self._generate_billing_alerts(consumption, overage_charges, days_remaining)
        }

    def _generate_billing_alerts(self, consumption, overage_charges, days_remaining):
        """Generar alertas de facturación relevantes"""
        alerts = []

        if consumption.data_usage_percentage > 90:
            alerts.append({
                'type': 'warning',
                'message': f'Has usado el {consumption.data_usage_percentage:.1f}% de tus datos',
                'action': 'Considera renovar tu plan o comprar datos adicionales'
            })

        if consumption.minutes_usage_percentage > 85:
            alerts.append({
                'type': 'info',
                'message': f'Has usado el {consumption.minutes_usage_percentage:.1f}% de tus minutos',
                'action': 'Monitorea tu uso para evitar cargos adicionales'
            })

        if overage_charges > 0:
            alerts.append({
                'type': 'error',
                'message': f'Tienes cargos adicionales de ${overage_charges:.2f}',
                'action': 'Revisa tu uso y considera cambiar de plan'
            })

        if days_remaining <= 5:
            alerts.append({
                'type': 'info',
                'message': f'Tu ciclo de facturación termina en {days_remaining} días',
                'action': 'Tu uso se reiniciará pronto'
            })

        if consumption.account_balance < 10:
            alerts.append({
                'type': 'warning',
                'message': f'Saldo bajo: ${consumption.account_balance:.2f}',
                'action': 'Recarga tu cuenta para evitar interrupciones'
            })

        return alerts


class CustomersListAPI(Resource):
    """API para lista de clientes"""

    def get(self):
        """
        Obtener lista de clientes con paginación

        Query params:
        - page: número de página (default: 1)
        - limit: clientes por página (default: 10)
        - search: término de búsqueda (opcional)
        """
        try:
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 10, type=int)
            search = request.args.get('search', '')

            limit = min(limit, 50)

            query = Customer.query

            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    db.or_(
                        Customer.name.ilike(search_filter),
                        Customer.email.ilike(search_filter),
                        Customer.phone.ilike(search_filter),
                        Customer.plan_type.ilike(search_filter)
                    )
                )

            offset = (page - 1) * limit
            customers_query = query.offset(offset).limit(limit)
            customers = customers_query.all()

            total_customers = query.count()

            customers_data = []
            for customer in customers:
                customer_dict = customer.to_dict()

                consumption = Consumption.query.filter_by(customer_id=customer.id).first()
                if consumption:
                    customer_dict['consumption_summary'] = {
                        'data_usage_percentage': consumption.data_usage_percentage,
                        'minutes_usage_percentage': consumption.minutes_usage_percentage,
                        'account_balance': consumption.account_balance,
                        'status': self._get_customer_status(consumption)
                    }
                else:
                    customer_dict['consumption_summary'] = {
                        'data_usage_percentage': 0,
                        'minutes_usage_percentage': 0,
                        'account_balance': 0,
                        'status': 'no_data'
                    }

                customers_data.append(customer_dict)

            logger.info(f"Customers list retrieved: page {page}, {len(customers_data)} customers")
            return {
                'success': True,
                'data': customers_data,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_customers,
                    'pages': (total_customers + limit - 1) // limit,
                    'hasNext': page * limit < total_customers,
                    'hasPrev': page > 1
                }
            }, 200

        except Exception as e:
            logger.error(f"Error getting customers list: {e}")
            return {'error': 'Error interno del servidor'}, 500

    def _get_customer_status(self, consumption):
        """Determinar el estado del cliente basado en su consumo"""
        if consumption.account_balance <= 0:
            return 'suspended'
        elif consumption.data_usage_percentage > 100 or consumption.minutes_usage_percentage > 100:
            return 'overage'
        elif consumption.data_usage_percentage > 90 or consumption.minutes_usage_percentage > 90:
            return 'warning'
        else:
            return 'active'


class BSSystemStatusAPI(Resource):
    """API mejorada para verificar el estado del sistema BSS"""

    def __init__(self):
        self.bss_simulator = BSSSimulator()

    def get(self):
        """Obtener estado actual del sistema BSS (compatible con SystemService frontend)"""
        try:
            bss_status = self.bss_simulator.check_bss_status()

            db_status = self._check_database_status()
            api_status = self._get_api_status()

            system_status = {
                'bss': {
                    'status': bss_status.get('status', 'unknown'),
                    'responseTime': int(bss_status.get('response_time', '0ms').replace('ms', '')),
                    'lastCheck': datetime.utcnow().isoformat(),
                    'services': {
                        'billing': 'operational' if bss_status.get('status') == 'online' else 'degraded',
                        'provisioning': 'operational',
                        'customer_data': 'operational',
                        'reporting': 'operational' if random.random() > 0.1 else 'maintenance'
                    }
                },
                'database': db_status,
                'api': api_status
            }

            logger.info("System status retrieved successfully")
            return {
                'success': True,
                'data': system_status
            }, 200

        except Exception as e:
            logger.error(f"Error checking system status: {e}")
            return {
                'success': False,
                'error': 'Error verificando estado del sistema',
                'data': {
                    'bss': {
                        'status': 'offline',
                        'responseTime': 0,
                        'lastCheck': datetime.utcnow().isoformat(),
                        'services': {}
                    },
                    'database': {'status': 'unknown', 'connections': 0},
                    'api': {'status': 'error', 'version': '1.0.0', 'uptime': 0}
                }
            }, 500

    def _check_database_status(self):
        """Verificar estado de la base de datos"""
        try:
            db.session.execute(db.text('SELECT 1'))
            return {
                'status': 'healthy',
                'connections': random.randint(3, 12),
                'responseTime': random.randint(1, 5),
                'lastBackup': (datetime.now() - timedelta(hours=random.randint(1, 12))).isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'error',
                'connections': 0,
                'responseTime': 0,
                'error': str(e)
            }

    def _get_api_status(self):
        """Obtener estado de la API"""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'uptime': round(random.uniform(95.0, 99.9), 2),
            'requestsPerMinute': random.randint(50, 200),
            'averageResponseTime': random.randint(50, 150),
            'activeConnections': random.randint(10, 45)
        }