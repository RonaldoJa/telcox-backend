import os
import random
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BSSSimulator:
    """
    Simulador del sistema BSS (Business Support System)
    Simula la integración con un sistema BSS real
    """

    def __init__(self):
        self.simulation_delay = float(os.getenv('BSS_SIMULATION_DELAY', 0.1))
        self.failure_rate = float(os.getenv('BSS_FAILURE_RATE', 0.05))
        self.last_check_time = None
        self.cached_status = None

    def get_customer_consumption(self, customer_id):
        """
        Simula la obtención de datos de consumo desde el sistema BSS

        Args:
            customer_id (int): ID del cliente

        Returns:
            dict: Datos de consumo o None si hay error
        """
        try:
            time.sleep(self.simulation_delay)

            if random.random() < self.failure_rate:
                logger.warning(f"BSS connection failed for customer {customer_id}")
                return None

            consumption_data = self._generate_realistic_data(customer_id)

            logger.info(f"BSS data retrieved successfully for customer {customer_id}")
            return consumption_data

        except Exception as e:
            logger.error(f"BSS simulation error for customer {customer_id}: {str(e)}")
            return None

    def _generate_realistic_data(self, customer_id):
        """Generar datos realistas de consumo"""
        current_hour = datetime.now().hour
        usage_multiplier = self._get_usage_multiplier(current_hour)

        base_data_usage = random.uniform(800, 4200)
        base_minutes_usage = random.randint(60, 420)
        base_balance = random.uniform(8.0, 45.0)

        timestamp_variance = int(time.time()) % 60
        data_variance = timestamp_variance * 12 * usage_multiplier

        return {
            'customer_id': customer_id,
            'data_used_mb': round(base_data_usage + data_variance, 2),
            'minutes_used': int(base_minutes_usage + (timestamp_variance // 8) * usage_multiplier),
            'account_balance': round(base_balance + (timestamp_variance * 0.08), 2),
            'last_sync': datetime.utcnow().isoformat(),
            'bss_status': 'online',
            'sync_quality': random.choice(['high', 'medium', 'low']),
            'response_time_ms': int(self.simulation_delay * 1000),
            'connection_type': random.choice(['4G', '5G', 'LTE']),
            'signal_strength': random.randint(70, 95)
        }

    def _get_usage_multiplier(self, hour):
        """Calcular multiplicador de uso basado en la hora"""
        if 9 <= hour <= 17:  
            return 1.3
        elif 19 <= hour <= 22:  
            return 1.1
        elif 0 <= hour <= 6:  
            return 0.3
        else:
            return 0.7

    def check_bss_status(self):
        """Verificar estado del sistema BSS con cache"""
        try:
            now = time.time()
            if (self.last_check_time and
                    now - self.last_check_time < 30 and
                    self.cached_status):
                return self.cached_status

            time.sleep(0.05)  

            if random.random() < 0.02: 
                status = {
                    'status': 'down',
                    'message': 'BSS temporarily unavailable',
                    'estimated_recovery': '5 minutes',
                    'last_successful_check': self.last_check_time,
                    'error_code': 'BSS_CONNECTION_TIMEOUT',
                    'response_time': 'timeout'
                }
            elif random.random() < 0.05:  
                status = {
                    'status': 'degraded',
                    'message': 'BSS experiencing high latency',
                    'response_time': f"{random.randint(800, 2000)}ms",
                    'affected_services': ['billing', 'provisioning'],
                    'severity': 'medium'
                }
            else:
                # Estado normal
                response_time = int(self.simulation_delay * 1000)
                status = {
                    'status': 'online',
                    'message': 'BSS operational',
                    'response_time': f"{response_time}ms",
                    'services_status': {
                        'billing': 'operational',
                        'provisioning': 'operational',
                        'customer_data': 'operational',
                        'reporting': random.choice(['operational', 'maintenance'])
                    },
                    'performance_metrics': {
                        'avg_response_time': response_time,
                        'success_rate': round(random.uniform(95.0, 99.9), 2),
                        'active_connections': random.randint(50, 200)
                    }
                }

            self.last_check_time = now
            self.cached_status = status

            logger.info(f"BSS status check completed: {status['status']}")
            return status

        except Exception as e:
            logger.error(f"Error checking BSS status: {e}")
            return {
                'status': 'error',
                'message': 'Unable to check BSS status',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_network_quality_metrics(self, customer_id):
        """
        Simular métricas de calidad de red para un cliente

        Args:
            customer_id (int): ID del cliente

        Returns:
            dict: Métricas de calidad de red
        """
        try:
            time.sleep(0.02)  

            current_hour = datetime.now().hour

            if 18 <= current_hour <= 22:
                latency_base = random.uniform(25, 50)
                speed_factor = random.uniform(0.6, 0.8)
                packet_loss = random.uniform(0.1, 1.0)
            else:
                latency_base = random.uniform(10, 25)
                speed_factor = random.uniform(0.8, 1.0)
                packet_loss = random.uniform(0.0, 0.3)

            return {
                'customer_id': customer_id,
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': {
                    'download_speed_mbps': round(100 * speed_factor * random.uniform(0.9, 1.1), 1),
                    'upload_speed_mbps': round(50 * speed_factor * random.uniform(0.9, 1.1), 1),
                    'latency_ms': round(latency_base, 1),
                    'jitter_ms': round(random.uniform(1, 8), 1),
                    'packet_loss_percent': round(packet_loss, 2),
                    'signal_strength_dbm': random.randint(-85, -45),
                    'connection_stability': self._assess_connection_stability(latency_base, packet_loss)
                },
                'location_info': {
                    'cell_tower_id': f"GYE{random.randint(100, 999)}",
                    'coverage_type': random.choice(['excellent', 'good', 'fair']),
                    'estimated_distance_m': random.randint(200, 2000)
                }
            }

        except Exception as e:
            logger.error(f"Error getting network metrics for customer {customer_id}: {e}")
            return None

    def _assess_connection_stability(self, latency, packet_loss):
        """Evaluar estabilidad de conexión basada en métricas"""
        if latency < 20 and packet_loss < 0.1:
            return 'excellent'
        elif latency < 35 and packet_loss < 0.5:
            return 'good'
        elif latency < 50 and packet_loss < 1.0:
            return 'fair'
        else:
            return 'poor'

    def simulate_real_time_update(self, customer_id):
        """
        Simular actualización en tiempo real de datos del cliente

        Args:
            customer_id (int): ID del cliente

        Returns:
            dict: Datos actualizados
        """
        base_data = self.get_customer_consumption(customer_id)
        if not base_data:
            return None

        base_data.update({
            'real_time_usage': {
                'current_session_mb': round(random.uniform(0.5, 15.0), 2),
                'session_duration_minutes': random.randint(1, 45),
                'active_applications': random.choice([
                    ['WhatsApp', 'Chrome'],
                    ['YouTube', 'Instagram'],
                    ['Zoom', 'Teams'],
                    ['Netflix', 'Spotify'],
                    ['Maps', 'Chrome']
                ]),
                'quality_of_experience': random.choice(['excellent', 'good', 'fair', 'poor'])
            },
            'predictions': {
                'estimated_monthly_usage_mb': round(base_data['data_used_mb'] * 1.5, 2),
                'days_until_limit': random.randint(5, 25),
                'recommended_action': random.choice([
                    'continue_normal_usage',
                    'monitor_usage',
                    'consider_upgrade',
                    'reduce_usage'
                ])
            }
        })

        return base_data