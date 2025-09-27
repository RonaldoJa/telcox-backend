# app/models/customer.py
from app import db  # Importar desde app/__init__.py
from datetime import datetime
from sqlalchemy import func


class Customer(db.Model):
    """Modelo para información de clientes"""
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    consumptions = db.relationship('Consumption', backref='customer', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Customer {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'plan_type': self.plan_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Consumption(db.Model):
    """Modelo para datos de consumo de clientes"""
    __tablename__ = 'consumptions'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    data_used_mb = db.Column(db.Float, default=0.0)
    data_limit_mb = db.Column(db.Float, nullable=False)
    minutes_used = db.Column(db.Integer, default=0)
    minutes_limit = db.Column(db.Integer, nullable=False)
    account_balance = db.Column(db.Float, default=0.0)
    billing_cycle_start = db.Column(db.Date, nullable=False)
    billing_cycle_end = db.Column(db.Date, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Consumption Customer:{self.customer_id}>'

    @property
    def data_remaining_mb(self):
        """Calcular datos restantes"""
        return max(0, self.data_limit_mb - self.data_used_mb)

    @property
    def data_usage_percentage(self):
        """Calcular porcentaje de uso de datos"""
        if self.data_limit_mb <= 0:
            return 0
        return min(100, (self.data_used_mb / self.data_limit_mb) * 100)

    @property
    def minutes_remaining(self):
        """Calcular minutos restantes"""
        return max(0, self.minutes_limit - self.minutes_used)

    @property
    def minutes_usage_percentage(self):
        """Calcular porcentaje de uso de minutos"""
        if self.minutes_limit <= 0:
            return 0
        return min(100, (self.minutes_used / self.minutes_limit) * 100)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'data_used_mb': round(self.data_used_mb, 2),
            'data_limit_mb': round(self.data_limit_mb, 2),
            'data_remaining_mb': round(self.data_remaining_mb, 2),
            'data_usage_percentage': round(self.data_usage_percentage, 2),
            'minutes_used': self.minutes_used,
            'minutes_limit': self.minutes_limit,
            'minutes_remaining': self.minutes_remaining,
            'minutes_usage_percentage': round(self.minutes_usage_percentage, 2),
            'account_balance': round(self.account_balance, 2),
            'billing_cycle_start': self.billing_cycle_start.isoformat() if self.billing_cycle_start else None,
            'billing_cycle_end': self.billing_cycle_end.isoformat() if self.billing_cycle_end else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }