# 🚀 TelcoX 
## Resumen 

**TelcoX** es una plataforma completa de autogestión para servicios de telecomunicaciones que permite a los clientes consultar su consumo de datos, minutos y saldo en tiempo real. La solución incluye integración simulada con sistemas BSS, interfaz intuitiva y capacidades de monitoreo en tiempo real.

### ✨ Características Principales

- **Dashboard en tiempo real** con actualización automática
- **Visualización intuitiva** de consumo de datos y minutos
- **Integración con sistema BSS** (simulado con latencia real)
- **Alertas inteligentes** cuando se alcanzan límites de consumo
- **Arquitectura escalable** con Docker y microservicios
- **API RESTful** bien documentada

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Frontend** | Angular + Bootstrap | 16+ |
| **Backend** | Python Flask + SQLAlchemy | 3.9+ |
| **Base de Datos** | MySQL | 8.0+ |
| **Contenerización** | Docker + Docker Compose | Latest |

## 📁 Estructura del Proyecto

```
telcox-platform/
├── 📄 README.md                    # Este archivo
├── 📄 docker-compose.yml           # Configuración de Docker
├── 📄 .env.example                 # Variables de entorno
├── 
├── 📁 backend/                     # API Flask
│   ├── 📄 app.py                  # Punto de entrada
│   ├── 📄 requirements.txt        # Dependencias Python
│   ├── 📄 Dockerfile              # Imagen Docker del backend
│   ├── 📁 app/
│   │   ├── 📄 __init__.py         # Configuración de Flask
│   │   ├── 📁 models/             # Modelos de datos
│   │   ├── 📁 apis/               # Endpoints de API
│   │   └── 📁 services/           # Lógica de negocio
│   └── 📁 tests/                   # Pruebas unitarias
│
├── 📁 frontend/                    # Aplicación Angular
│   ├── 📄 package.json            # Dependencias Node.js
│   ├── 📄 Dockerfile              # Imagen Docker del frontend
│   ├── 📄 angular.json            # Configuración Angular
│   └── 📁 src/
│       ├── 📁 app/
│       │   ├── 📁 components/     # Componentes Angular
│       │   ├── 📁 services/       # Servicios HTTP
│       │   └── 📁 models/         # Modelos TypeScript
│       └── 📁 environments/        # Configuración de entornos
│
└── 📁 docs/                        # Documentación adicional
```

## 🚀 Instalación y Ejecución

### Opción 1: Docker (Recomendado) 🐳

**Requisitos previos:**
- Docker Desktop instalado
- Git instalado

```bash
# 1. Clonar el repositorio
git clone https://github.com/RonaldoJa/telcox-frontend
git clone https://github.com/RonaldoJa/telcox-backend
unificar ambas carpetas  

o

Desargar los archivos adjuntos en el Drive https://drive.google.com/drive/folders/16ndDw_Di5qyYMoiRB9qWJeYwAy0Jh8fO

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Ejecutar con Docker Compose
docker-compose up --build

# 4. Acceder a la aplicación
# Frontend: http://localhost
# Backend API: http://localhost:5100
# Base de datos: localhost:3306
```

### Opción 2: Instalación Manual 🔧

#### Prerrequisitos
- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- npm o yarn

#### Backend Setup

```bash
# 1. Navegar al directorio del backend
cd backend

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar base de datos MySQL
mysql -u root -p
CREATE DATABASE telcox_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'telcox_user'@'localhost' IDENTIFIED BY 'telcox_pass';
GRANT ALL PRIVILEGES ON telcox_db.* TO 'telcox_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 6. Configurar variables de entorno
export DATABASE_URL="mysql+pymysql://telcox_user:telcox_pass@localhost/telcox_db"
export FLASK_ENV=development
export SECRET_KEY=your-secret-key-here

# 7. Ejecutar la aplicación
python app.py
```

#### Frontend Setup

```bash
# 1. Navegar al directorio del frontend
cd frontend

# 2. Instalar dependencias
npm install

# 3. Ejecutar en modo desarrollo
ng serve

# 4. La aplicación estará disponible en http://localhost:4200
```

## 🧪 Ejecutar Pruebas

### Pruebas del Backend (pytest)

```bash
cd backend

# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Ejecutar con reporte de cobertura
python -m pytest tests/ -v --cov=app --cov-report=html

# Ejecutar pruebas específicas
python -m pytest tests/test_customer_routes.py -v
```

### Pruebas del Frontend (Jest)

```bash
cd frontend

# Ejecutar todas las pruebas
npm test

# Ejecutar con cobertura
npm run test:coverage

# Ejecutar en modo watch
npm run test:watch
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=mysql+pymysql://telcox_user:telcox_pass@database/telcox_db
MYSQL_ROOT_PASSWORD=root_password_secure_123
MYSQL_DATABASE=telcox_db
MYSQL_USER=telcox_user
MYSQL_PASSWORD=telcox_pass_secure_456

# Flask
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura-aqui

# API Configuration
API_URL=http://localhost:5000/api
PORT=5000

# BSS Simulator Settings
BSS_SIMULATION_DELAY=0.1
BSS_FAILURE_RATE=0.05
```

## 📖 Documentación de la API

### Endpoints Disponibles

#### 🔍 GET `/api/customers/{customer_id}`
Obtiene información básica del cliente.

**Parámetros:**
- `customer_id` (integer): ID único del cliente

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "phone": "+593987654321",
    "plan_type": "Premium",
    "created_at": "2025-01-01T00:00:00.000Z"
  }
}
```

**Errores posibles:**
- `404`: Cliente no encontrado
- `500`: Error interno del servidor

#### 📊 GET `/api/customers/{customer_id}/consumption`
Obtiene datos de consumo del cliente en tiempo real.

**Parámetros:**
- `customer_id` (integer): ID único del cliente

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "customer": {
      "id": 1,
      "name": "Juan Pérez",
      "email": "juan.perez@example.com",
      "phone": "+593987654321",
      "plan_type": "Premium"
    },
    "consumption": {
      "data_used_mb": 1500.0,
      "data_limit_mb": 5120.0,
      "data_remaining_mb": 3620.0,
      "data_usage_percentage": 29.3,
      "minutes_used": 180,
      "minutes_limit": 500,
      "minutes_remaining": 320,
      "minutes_usage_percentage": 36.0,
      "account_balance": 25.50,
      "billing_cycle_start": "2025-01-01",
      "billing_cycle_end": "2025-01-31",
      "last_updated": "2025-01-15T10:30:00.000Z"
    },
    "real_time_data": {
      "bss_status": "online",
      "last_sync": "2025-01-15T10:30:00.000Z"
    }
  }
}
```

**Errores posibles:**
- `404`: Cliente no encontrado
- `503`: Sistema BSS no disponible
- `500`: Error interno del servidor

## 📊 Monitoreo y Métricas

### Health Check
```bash
# Verificar estado del backend
curl http://localhost:5000/api/health

# Verificar estado de la base de datos
curl http://localhost:5000/api/db-status
```

### Logs
```bash
# Ver logs del backend
docker-compose logs -f backend

# Ver logs del frontend
docker-compose logs -f frontend

# Ver logs de la base de datos
docker-compose logs -f database
```

## 🐛 Solución de Problemas

### Problemas Comunes

#### Error: "Connection refused" al backend
```bash
# Verificar que el backend esté corriendo
docker-compose ps

# Reiniciar servicios
docker-compose restart backend
```

#### Error: "Can't connect to MySQL server"
```bash
# Verificar configuración de base de datos
docker-compose logs database

# Recrear volumen de base de datos
docker-compose down -v
docker-compose up --build
```

#### Frontend no carga datos
```bash
# Verificar configuración del API_URL
cat frontend/src/environments/environment.ts

# Verificar CORS en el backend
curl -H "Origin: http://localhost:4200" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:5000/api/customers/1
```

### Debug del Sistema BSS

El simulador BSS puede configurarse para diferentes comportamientos:

```python
# En app/services/bss_simulator.py
class BSSSimulator:
    def __init__(self):
        self.simulation_delay = 0.1      # Latencia simulada
        self.failure_rate = 0.05         # 5% de fallos
        self.timeout_duration = 5.0      # Timeout en segundos
```

## 🔒 Seguridad

### Consideraciones de Seguridad Implementadas

- **CORS configurado** para permitir solo orígenes autorizados
- **Validación de entrada** en todos los endpoints
- **Manejo seguro de errores** sin exposición de información sensible
- **Variables de entorno** para credenciales de base de datos
- **Logs estructurados** para auditoria
