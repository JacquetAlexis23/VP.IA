#!/bin/bash
# Script de despliegue para VP-Ai

echo "🚀 Iniciando despliegue de VP-Ai..."

# Verificar que existe .env
if [ ! -f .env ]; then
    echo "❌ Error: Archivo .env no encontrado"
    echo "📝 Copia .env.example a .env y configura las variables"
    exit 1
fi

# Verificar OPENROUTER_API_KEY
if ! grep -q "OPENROUTER_API_KEY=sk-or-v1-" .env; then
    echo "❌ Error: OPENROUTER_API_KEY no configurada en .env"
    exit 1
fi

echo "✅ Variables de entorno configuradas"

# Verificar que existe app.py
if [ ! -f app.py ]; then
    echo "❌ Error: app.py no encontrado"
    exit 1
fi

# Verificar que existe el JSON de documentos
if [ ! -f docs/rag_documents.json ]; then
    echo "❌ Error: docs/rag_documents.json no encontrado"
    echo "📝 Ejecuta ./update_docs.sh para generar la base de conocimiento"
    exit 1
fi

echo "✅ Base de conocimiento JSON encontrada"

# Verificar instalación de dependencias
echo "📦 Verificando dependencias..."
python -c "import streamlit, pypdf, requests, pydantic; print('✅ Dependencias OK')"

# Verificar que el sistema carga correctamente
echo "🔍 Verificando carga del sistema..."
python -c "
import sys
sys.path.append('src')
from rag_system import RAGSystem
rag = RAGSystem()
print(f'✅ Sistema RAG: {len(rag.documents)} documentos cargados')
"

echo ""
echo "🎉 ¡Listo para despliegue!"
echo ""
echo "Para desplegar en Streamlit Cloud:"
echo "1. Sube este código a GitHub (solo el JSON, no los PDFs grandes)"
echo "2. Ve a https://share.streamlit.io"
echo "3. Conecta tu repositorio"
echo "4. Configura main file: app.py"
echo "5. Deploy!"
echo ""
echo "📚 La versión online tendrá acceso a TODOS los documentos técnicos"
echo "   gracias al archivo rag_documents.json preprocesado"
echo ""
echo "URL de producción: https://tu-app.streamlit.app"