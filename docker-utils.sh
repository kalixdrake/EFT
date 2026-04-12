#!/bin/bash
# Script de Utilidades para Gestión de Contenedores EFT
# Uso: ./docker-utils.sh [comando]

set -e

# Ejecutar siempre desde la raíz del repositorio (donde vive docker-compose.yml)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de ayuda
show_help() {
    echo -e "${GREEN}=== EFT Docker Utils ===${NC}"
    echo ""
    echo "Comandos disponibles:"
    echo ""
    echo "  ${YELLOW}start${NC}         - Iniciar servicios en modo desarrollo"
    echo "  ${YELLOW}stop${NC}          - Detener servicios"
    echo "  ${YELLOW}restart${NC}       - Reiniciar servicios"
    echo "  ${YELLOW}logs${NC}          - Ver logs de todos los servicios"
    echo "  ${YELLOW}logs-web${NC}      - Ver logs del servicio web"
    echo "  ${YELLOW}logs-db${NC}       - Ver logs de la base de datos"
    echo "  ${YELLOW}status${NC}        - Ver estado de los servicios"
    echo "  ${YELLOW}shell${NC}         - Abrir shell de Django"
    echo "  ${YELLOW}bash${NC}          - Abrir bash en el contenedor web"
    echo "  ${YELLOW}dbshell${NC}       - Conectar a PostgreSQL"
    echo "  ${YELLOW}migrate${NC}       - Ejecutar migraciones"
    echo "  ${YELLOW}makemigrations${NC} - Crear nuevas migraciones"
    echo "  ${YELLOW}createsuperuser${NC} - Crear usuario administrador"
    echo "  ${YELLOW}collectstatic${NC} - Recolectar archivos estáticos"
    echo "  ${YELLOW}test${NC}          - Ejecutar tests"
    echo "  ${YELLOW}backup${NC}        - Hacer backup de la base de datos"
    echo "  ${YELLOW}clean${NC}         - Limpiar contenedores y volúmenes"
    echo "  ${YELLOW}prod-start${NC}    - Iniciar en modo producción"
    echo "  ${YELLOW}prod-stop${NC}     - Detener modo producción"
    echo ""
}

# Verificar que docker compose esté disponible
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker no está instalado${NC}"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}Error: Docker Compose no está disponible${NC}"
        exit 1
    fi
}

# Comandos
case "$1" in
    start)
        echo -e "${GREEN}Iniciando servicios en modo desarrollo...${NC}"
        docker compose up -d --build
        echo -e "${GREEN}Servicios iniciados. Accede a: http://localhost:8000${NC}"
        ;;
    
    stop)
        echo -e "${YELLOW}Deteniendo servicios...${NC}"
        docker compose stop
        ;;
    
    restart)
        echo -e "${YELLOW}Reiniciando servicios...${NC}"
        docker compose restart
        ;;
    
    logs)
        docker compose logs -f
        ;;
    
    logs-web)
        docker compose logs -f web
        ;;
    
    logs-db)
        docker compose logs -f db
        ;;
    
    status)
        docker compose ps
        ;;
    
    shell)
        docker compose exec web python manage.py shell
        ;;
    
    bash)
        docker compose exec web bash
        ;;
    
    dbshell)
        docker compose exec db psql -U eft_user -d eft_db
        ;;
    
    migrate)
        echo -e "${GREEN}Ejecutando migraciones...${NC}"
        docker compose exec web python manage.py migrate
        ;;
    
    makemigrations)
        echo -e "${GREEN}Creando migraciones...${NC}"
        docker compose exec web python manage.py makemigrations
        ;;
    
    createsuperuser)
        docker compose exec web python manage.py createsuperuser
        ;;
    
    collectstatic)
        echo -e "${GREEN}Recolectando archivos estáticos...${NC}"
        docker compose exec web python manage.py collectstatic --noinput
        ;;
    
    test)
        echo -e "${GREEN}Ejecutando tests...${NC}"
        docker compose exec web python manage.py test
        ;;
    
    backup)
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        echo -e "${GREEN}Creando backup: ${BACKUP_FILE}${NC}"
        docker compose exec db pg_dump -U eft_user eft_db > "$BACKUP_FILE"
        echo -e "${GREEN}Backup creado exitosamente${NC}"
        ;;
    
    clean)
        echo -e "${RED}¿Estás seguro? Esto eliminará todos los contenedores y volúmenes. (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            docker compose down -v
            echo -e "${GREEN}Limpieza completada${NC}"
        fi
        ;;
    
    prod-start)
        if [ ! -f ".env.prod" ]; then
            echo -e "${RED}Error: .env.prod no encontrado${NC}"
            exit 1
        fi
        echo -e "${GREEN}Iniciando en modo PRODUCCIÓN...${NC}"
        docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
        ;;
    
    prod-stop)
        docker compose -f docker-compose.prod.yml stop
        ;;
    
    *)
        show_help
        ;;
esac

check_docker
