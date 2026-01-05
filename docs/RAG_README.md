# 📚 Sistema RAG - Base de Conocimiento

El sistema RAG (Retrieval-Augmented Generation) alimenta al agente con información técnica sobre implementos y mini cargadoras.

## 📁 Estructura de Archivos

```
docs/
├── rag_documents.json    # Base de conocimiento (JSON)
├── manuals/             # Directorio para manuales
│   ├── Bobcat_S70_Manual.pdf
│   ├── Caterpillar_Compatibilidad.txt
│   └── ...
└── *.txt                # Archivos de ejemplo
```

## 🤖 Cómo Alimentar el RAG

### Opción 1: Usar el Gestor Interactivo
```bash
python rag_manager.py
```

### Opción 2: Cargar desde Archivos

#### Archivos de Texto (.txt, .md)
Crea archivos en `docs/manuals/` con contenido técnico:

**Ejemplo: `Bobcat_S70_Especificaciones.txt`**
```
Bobcat S70 - Especificaciones Técnicas

Capacidad de carga: 320kg
Sistema hidráulico: 45L/min a 2.400 psi
Compatible con:
- Baldes hasta 0.3m³
- Martillos hasta 300kg
- Horquillas pallet
```

#### Archivos PDF
Coloca tus manuales PDF en `docs/manuals/` y el sistema extraerá automáticamente el texto.

#### Formato JSON
Edita `docs/rag_documents.json` directamente:

```json
{
  "documents": [
    {
      "id": "doc_001",
      "content": "Contenido técnico completo...",
      "metadata": {
        "marca": "Bobcat",
        "modelo": "S70",
        "categoria": "especificaciones"
      }
    }
  ]
}
```

## 🏷️ Metadata Automática

El sistema extrae metadata automáticamente del nombre del archivo:

- **Marcas**: Bobcat, Caterpillar, John Deere, etc.
- **Modelos**: S70, 242D, 2025R, etc.
- **Categorías**: especificaciones, compatibilidad, manual, instalacion

**Ejemplos de nombres de archivo:**
- `Bobcat_S70_Especificaciones.pdf` → `{"marca": "Bobcat", "modelo": "S70", "categoria": "especificaciones"}`
- `Caterpillar_Compatibilidad.txt` → `{"marca": "Caterpillar", "categoria": "compatibilidad"}`

## 🔍 Cómo Funciona en el Agente

1. **Usuario pregunta**: "Necesito un martillo para mi Bobcat S70"
2. **Agente extrae**: marca="Bobcat", modelo="S70", implemento="martillo"
3. **RAG busca**: Documentos relevantes sobre Bobcat S70 y martillos
4. **LLM responde**: Con información técnica precisa del RAG

## 🚀 Próximos Pasos Avanzados

### Conectar con Pinecone (Recomendado)
Para bases de conocimiento grandes, conecta con Pinecone:

1. **Crear cuenta**: https://www.pinecone.io/
2. **Configurar en .env**:
   ```
   VECTOR_DB_URL=https://tu-index.pinecone.io
   PINECONE_API_KEY=tu_api_key
   PINECONE_ENVIRONMENT=us-west1-gcp
   ```
3. **El sistema usará automáticamente** embeddings vectoriales

### Embeddings Locales
Para funcionamiento completamente local:
```bash
pip install sentence-transformers
```

## 📊 Monitoreo

El agente registra qué documentos usa para cada consulta, permitiendo:
- Mejorar la base de conocimiento
- Identificar gaps en la información
- Optimizar respuestas

## 🆘 Solución de Problemas

**PDF no carga**: Verifica que tenga texto extraíble (no solo imágenes)
**Metadata incorrecta**: Renombra archivos con patrón Marca_Modelo_Categoria
**Búsqueda no funciona**: Verifica que los documentos tengan metadata correcta

---

**💡 Tip**: Comienza con archivos de texto simples, luego migra a PDFs y finalmente a Pinecone para escalabilidad.</content>
<parameter name="filePath">c:\Users\Ingenieria01\Desktop\VP-Ai\docs\RAG_README.md