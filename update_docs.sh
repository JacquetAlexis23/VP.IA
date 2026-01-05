#!/bin/bash
# Script para actualizar la base de conocimiento JSON
# Ejecutar cuando se agreguen nuevos documentos

echo "🔄 Actualizando base de conocimiento..."

# Verificar que existan documentos
if [ ! -d "docs/manuals" ]; then
    echo "❌ Error: Directorio docs/manuals no encontrado"
    exit 1
fi

# Procesar documentos y generar JSON
python -c "
import sys
sys.path.append('src')
from rag_system import RAGSystem
import json

print('Procesando documentos...')
rag = RAGSystem()

documents_data = []
for doc in rag.documents:
    documents_data.append({
        'id': doc.id,
        'content': doc.content,
        'metadata': doc.metadata
    })

with open('docs/rag_documents.json', 'w', encoding='utf-8') as f:
    json.dump({'documents': documents_data}, f, ensure_ascii=False, indent=2)

print(f'✅ Actualizados {len(documents_data)} documentos en docs/rag_documents.json')
"

echo "📄 Archivo JSON actualizado. Recuerda hacer commit de los cambios."