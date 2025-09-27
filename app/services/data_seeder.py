from app.models.customer import Customer, Consumption
from app import db
from datetime import datetime, date, timedelta
import logging
import os

logger = logging.getLogger(__name__)


def seed_test_data():
    """
    Insertar datos de prueba en la base de datos si no existen
    """
    try:
        if Customer.query.count() > 0:
            logger.info("Test data already exists, skipping seeding")
            return

        logger.info("Seeding test data...")

        customers_data = [
            {
                'name': 'Juan Carlos Pérez',
                'email': 'juan.perez@email.com',
                'phone': '+593 987 654 321',
                'plan_type': 'Premium',
                'data_limit': 5120,  # 5GB
                'minutes_limit': 500
            },
            {
                'name': 'María Elena González',
                'email': 'maria.gonzalez@email.com',
                'phone': '+593 976 543 210',
                'plan_type': 'Básico',
                'data_limit': 2048,  # 2GB
                'minutes_limit': 300
            },
            {
                'name': 'Carlos Roberto Rodríguez',
                'email': 'carlos.rodriguez@email.com',
                'phone': '+593 965 432 109',
                'plan_type': 'Empresarial',
                'data_limit': 10240,  # 10GB
                'minutes_limit': 1000
            },
            {
                'name': 'Ana Sofía Mendoza',
                'email': 'ana.mendoza@email.com',
                'phone': '+593 954 321 098',
                'plan_type': 'Familiar',
                'data_limit': 7168,  # 7GB
                'minutes_limit': 750
            }
        ]

        created_customers = []

        for customer_data in customers_data:
            customer = Customer(
                name=customer_data['name'],
                email=customer_data['email'],
                phone=customer_data['phone'],
                plan_type=customer_data['plan_type']
            )

            db.session.add(customer)
            db.session.flush()

            consumption = create_consumption_data(
                customer.id,
                customer_data['data_limit'],
                customer_data['minutes_limit']
            )

            db.session.add(consumption)
            created_customers.append(customer)

        db.session.commit()

        logger.info(f"Successfully seeded {len(created_customers)} customers with consumption data")

        for customer in created_customers:
            consumption = Consumption.query.filter_by(customer_id=customer.id).first()
            logger.info(f"Created: {customer.name} ({customer.plan_type}) - "
                        f"Data: {consumption.data_usage_percentage:.1f}%, "
                        f"Minutes: {consumption.minutes_usage_percentage:.1f}%")

    except Exception as e:
        logger.error(f"Error seeding test data: {e}")
        db.session.rollback()
        raise


def create_consumption_data(customer_id, data_limit_mb, minutes_limit):
    """
    Crear datos de consumo realistas para un cliente

    Args:
        customer_id (int): ID del cliente
        data_limit_mb (int): Límite de datos en MB
        minutes_limit (int): Límite de minutos

    Returns:
        Consumption: Objeto de consumo creado
    """
    import random

    data_usage_percentage = random.uniform(0.2, 0.85)
    minutes_usage_percentage = random.uniform(0.15, 0.80)

    data_used = data_limit_mb * data_usage_percentage
    minutes_used = int(minutes_limit * minutes_usage_percentage)

    account_balance = random.uniform(5.0, 50.0)

    today = date.today()
    billing_start = today.replace(day=1)

    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)

    billing_end = next_month - timedelta(days=1)

    return Consumption(
        customer_id=customer_id,
        data_used_mb=round(data_used, 2),
        data_limit_mb=data_limit_mb,
        minutes_used=minutes_used,
        minutes_limit=minutes_limit,
        account_balance=round(account_balance, 2),
        billing_cycle_start=billing_start,
        billing_cycle_end=billing_end
    )


def reset_test_data():
    """
    Eliminar y recrear todos los datos de prueba
    ¡CUIDADO: Esto eliminará todos los datos existentes!
    """
    if os.getenv('FLASK_ENV') != 'development':
        raise Exception("reset_test_data() only allowed in development environment")

    try:
        logger.warning("Resetting all test data...")

        Consumption.query.delete()
        Customer.query.delete()
        db.session.commit()

        seed_test_data()

        logger.info("Test data reset completed successfully")

    except Exception as e:
        logger.error(f"Error resetting test data: {e}")
        db.session.rollback()
        raise