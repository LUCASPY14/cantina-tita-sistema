#!/bin/bash
# Script para iniciar desarrollo completo del sistema POS
# Archivo: iniciar_desarrollo.sh

echo "🚀 INICIANDO SISTEMA POS COMPLETO"
echo "================================="

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Verificando dependencias...${NC}"

# Verificar si Python está disponible
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python no encontrado${NC}"
    exit 1
fi

# Verificar si Node.js está disponible  
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencias OK${NC}"

# Función para limpiar procesos al salir
cleanup() {
    echo -e "\n${YELLOW}🛑 Deteniendo servidores...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Configurar trap para limpiar al salir
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}🔧 Activando entorno virtual...${NC}"
# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
else
    echo -e "${YELLOW}⚠️  No se encontró entorno virtual${NC}"
fi

echo -e "${BLUE}🗄️  Iniciando servidor Django (Backend)...${NC}"
cd backend
python manage.py collectstatic --noinput > /dev/null 2>&1
python manage.py migrate --run-syncdb > /dev/null 2>&1
python manage.py runserver 8000 &
BACKEND_PID=$!
cd ..

# Esperar un momento para que Django se inicie
sleep 3

echo -e "${BLUE}🌐 Iniciando servidor Vite (Frontend)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ SERVIDORES INICIADOS${NC}"
echo "================================="
echo -e "${GREEN}🔗 Backend: http://localhost:8000${NC}"
echo -e "${GREEN}🔗 Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}🔗 POS Sistema: http://localhost:5173/pos-completo.html${NC}"
echo -e "${GREEN}🔗 API POS: http://localhost:8000/api/pos/${NC}"
echo "================================="
echo -e "${YELLOW}💡 Presiona Ctrl+C para detener ambos servidores${NC}"

# Esperar indefinidamente
wait