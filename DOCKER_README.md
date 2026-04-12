# EFT - Guía de Contenedorización con Docker

Esta guía te ayudará a ejecutar la aplicación Django EFT con PostgreSQL usando Docker y Docker Compose.

## 📋 Prerequisitos

- Docker (versión 20.10 o superior)
- Docker Compose (viene incluido con Docker Desktop)
- Git

## 🏗️ Arquitectura

La aplicación está dividida en los siguientes servicios:

### Desarrollo (backend desacoplado)
- **db**: PostgreSQL 16 (Alpine Linux)
- **web**: Django API (consumida por frontend web y app Flutter vía HTTP)

### Producción
- **db**: PostgreSQL 16 (Alpine Linux)
- **web**: Django con Gunicorn
- **nginx**: Proxy reverso y servidor de archivos estáticos

## 🚀 Inicio Rápido (Desarrollo)

### 1. Configurar Variables de Entorno

El archivo `.env.local` ya está configurado con valores por defecto para desarrollo:

```bash
# Ver configuración actual
cat .env.local
```

**⚠️ IMPORTANTE**: Estos valores son solo para desarrollo. Nunca uses estas credenciales en producción.

### 2. Iniciar los Servicios

```bash
# Construir y levantar los contenedores
docker compose up -d --build

# Ver los logs
docker compose logs -f

# Ver solo logs de un servicio específico
docker compose logs -f web
docker compose logs -f db
```

### 3. Ejecutar Migraciones

```bash
# Aplicar migraciones de la base de datos
docker compose exec web python manage.py migrate

# Recolectar archivos estáticos (opcional en desarrollo)
docker compose exec web python manage.py collectstatic --noinput
```

### 4. Crear Superusuario

```bash
# Método 1: Interactivo
docker compose exec web python manage.py createsuperuser

# Método 2: No interactivo (ya ejecutado)
# Usuario: admin, Password: [definir manualmente]
docker compose exec web python manage.py changepassword admin
```

### 5. Acceder a la Aplicación

- **API Backend**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin/
- **API Schema**: http://localhost:8000/api/schema/
- **Swagger UI**: http://localhost:8000/api/docs/

### 6. Chat IA seguro (autenticado + RBAC)

- Endpoint nuevo: `POST /api/interacciones/chat/`
- Requiere sesión iniciada (si no, responde `401`)
- Requiere capability RBAC `interaccion:create` (si no, responde `403`)
- El backend limita el contexto de IA a recursos permitidos por capability (no depende solo del prompt)

## 🔌 Integración frontend/web y móvil (Flutter)

Para mantener frontend y móvil livianos, deja toda la lógica de negocio en este backend y consume por requests HTTP.

Configura en `.env.local` los orígenes permitidos de tus apps cliente:

```bash
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=True
```

Si tu frontend/móvil usa sesión/cookies, mantén `CORS_ALLOW_CREDENTIALS=True` y agrega sus hosts también en:

```bash
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 🔧 Comandos Útiles

### Gestión de Contenedores

```bash
# Ver estado de los servicios
docker compose ps

# Detener los servicios
docker compose stop

# Detener y eliminar contenedores
docker compose down

# Detener y eliminar contenedores + volúmenes (⚠️ elimina la base de datos)
docker compose down -v

# Reconstruir un servicio específico
docker compose up -d --build web

# Reiniciar un servicio
docker compose restart web
```

### Gestión de Django

```bash
# Shell de Django
docker compose exec web python manage.py shell

# Crear migraciones
docker compose exec web python manage.py makemigrations

# Aplicar migraciones
docker compose exec web python manage.py migrate

# Crear app
docker compose exec web python manage.py startapp nombre_app

# Ejecutar tests
docker compose exec web python manage.py test

# Limpiar sesiones expiradas
docker compose exec web python manage.py clearsessions
```

### Gestión de Base de Datos

```bash
# Conectarse a PostgreSQL
docker compose exec db psql -U eft_user -d eft_db

# Backup de la base de datos
docker compose exec db pg_dump -U eft_user eft_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker compose exec -T db psql -U eft_user -d eft_db < backup_20260401.sql

# Ver logs de PostgreSQL
docker compose logs db
```

### Inspección y Debug

```bash
# Acceder al contenedor de Django
docker compose exec web bash

# Acceder al contenedor de PostgreSQL
docker compose exec db sh

# Ver uso de recursos
docker stats

# Inspeccionar volúmenes
docker volume ls
docker volume inspect copilot-worktree-2026-04-01t03-46-33_postgres_data
```

## 🌐 Despliegue en Producción

### 1. Configurar Variables de Entorno

Crea un archivo `.env.prod` con valores seguros:

```bash
# Django Configuration
DEBUG=False
DJANGO_SECRET_KEY=<genera-una-clave-secreta-fuerte-aqui>
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com

# Database Configuration
USE_SQLITE=False
DATABASE_ENGINE=postgresql
DATABASE_NAME=eft_db_prod
DATABASE_USERNAME=eft_user_prod
DATABASE_PASSWORD=<contraseña-fuerte-y-segura>
DATABASE_HOST=db
DATABASE_PORT=5432
```

### 2. Generar SECRET_KEY Segura

```bash
docker compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Iniciar en Producción

```bash
# Usar el archivo de composición de producción
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Aplicar migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Recolectar archivos estáticos
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Crear superusuario
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 4. Configurar HTTPS (Recomendado)

Para producción, se recomienda usar certificados SSL. Puedes usar Let's Encrypt con Certbot:

```bash
# Agregar certbot a docker-compose.prod.yml
# O configurar un balanceador de carga con SSL (AWS ELB, CloudFlare, etc.)
```

## 🔒 Seguridad

### Buenas Prácticas Implementadas

✅ **Usuario no-root**: La aplicación Django se ejecuta como usuario `appuser`  
✅ **Variables de entorno**: Credenciales y configuración en archivos .env  
✅ **Volúmenes nombrados**: Datos persistentes separados del código  
✅ **Health checks**: Monitoreo automático de la salud de PostgreSQL  
✅ **Gunicorn en producción**: Servidor WSGI robusto para producción  
✅ **Nginx como proxy**: Capa adicional de seguridad y rendimiento  
✅ **.dockerignore**: Evita copiar archivos sensibles al contenedor  

### Recomendaciones Adicionales

- 🔐 Cambia todas las contraseñas por defecto
- 🔑 Genera una SECRET_KEY única para producción
- 🚫 Nunca commitees archivos .env al repositorio
- 🔄 Mantén Docker y las imágenes actualizadas
- 📊 Configura logs centralizados
- 🛡️ Implementa rate limiting en Nginx
- 🔍 Activa auditoría y monitoreo

## 📦 Volúmenes

Los siguientes volúmenes persisten datos:

- `postgres_data`: Base de datos PostgreSQL
- `static_volume`: Archivos estáticos de Django
- `media_volume`: Archivos subidos por usuarios

```bash
# Listar volúmenes
docker volume ls | grep eft

# Backup de volumen
docker run --rm -v copilot-worktree-2026-04-01t03-46-33_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restaurar volumen
docker run --rm -v copilot-worktree-2026-04-01t03-46-33_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 🐛 Troubleshooting

### El contenedor no inicia

```bash
# Ver logs detallados
docker compose logs web
docker compose logs db

# Ver estado de salud
docker compose ps
```

### Error de conexión a la base de datos

```bash
# Verificar que la base de datos esté lista
docker compose exec db pg_isready -U eft_user

# Reiniciar servicios
docker compose restart db web
```

### Puerto 8000 ya en uso

```bash
# Ver qué está usando el puerto
sudo lsof -i :8000

# Cambiar el puerto en docker-compose.yml
# ports:
#   - "8001:8000"  # Usar 8001 en lugar de 8000
```

### Permisos de archivos

```bash
# Dar permisos al directorio de media
docker compose exec web chown -R appuser:appuser /app/media
```

## 🧹 Limpieza

```bash
# Detener y eliminar todo
docker compose down -v

# Eliminar imágenes no utilizadas
docker image prune -a

# Eliminar todo (⚠️ CUIDADO: elimina TODO de Docker)
docker system prune -a --volumes
```

## 📚 Recursos Adicionales

- [Documentación de Django](https://docs.djangoproject.com/)
- [Documentación de Docker](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker compose logs -f`
2. Verifica la configuración: `docker compose config`
3. Consulta la sección de Troubleshooting
4. Abre un issue en el repositorio

---

**Última actualización**: 2026-04-01
