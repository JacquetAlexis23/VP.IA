# 🚀 Agente Comercial Técnico B2B

Sistema de inteligencia artificial para calificación automatizada de leads B2B en empresa metalúrgica especializada en implementos para mini cargadoras y skid steers.

## 📋 Descripción

Este agente comercial automatiza el proceso de calificación de leads entrantes desde WhatsApp e Instagram, extrayendo información técnica de forma conversacional y preparando datos estructurados para el CRM Pilot.

### Características Principales

- ✅ **Máquina de estados** para gestión inteligente del flujo de conversación
- ✅ **Extracción automática** de datos técnicos (marca, modelo, implemento, zona)
- ✅ **Sistema RAG** para validación de compatibilidad técnica
- ✅ **Integración con Pilot CRM** para sincronización de leads
- ✅ **Scoring automático** de leads (A/B/C) según prioridad
- ✅ **Asignación inteligente** de vendedores por zona geográfica
- ✅ **Respuestas en JSON** estructurado para fácil integración

## � Despliegue Online

### Opción 1: Streamlit Cloud (Recomendado)

1. **Subir código a GitHub**
   ```bash
   # Crear repositorio en GitHub
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu-usuario/vp-ai.git
   git push -u origin main
   ```

2. **Configurar variables de entorno**
   - Copiar `.env.example` a `.env`
   - Configurar `OPENROUTER_API_KEY` con tu API key

3. **Desplegar en Streamlit Cloud**
   - Ir a [share.streamlit.io](https://share.streamlit.io)
   - Conectar tu repositorio de GitHub
   - Configurar:
     - **Main file path**: `app.py`
     - **Python version**: 3.11
   - Hacer clic en "Deploy"

4. **Configuración adicional**
   - El archivo `packages.txt` instala dependencias del sistema necesarias
   - El archivo `.streamlit/config.toml` configura el comportamiento en producción

### Opción 2: Heroku

1. **Crear archivo `Procfile`**
   ```
   web: streamlit run app.py --server.port $PORT --server.headless true
   ```

2. **Desplegar**
   ```bash
   heroku create tu-app-vp-ai
   git push heroku main
   ```

### Opción 3: VPS (DigitalOcean, AWS, etc.)

```bash
# Instalar dependencias
sudo apt update
sudo apt install python3.11 python3.11-venv poppler-utils tesseract-ocr tesseract-ocr-spa

# Configurar la aplicación
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ejecutar
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📚 Sistema de Documentos Optimizado

### Para Desarrollo Local
- **Documentos completos**: PDFs, imágenes y archivos técnicos en `docs/manuals/`
- **Procesamiento automático**: El sistema extrae texto de todos los archivos al iniciar

### Para Producción Online
- **Archivo JSON preprocesado**: `docs/rag_documents.json` (234KB vs 290MB)
- **Carga instantánea**: Sin procesamiento de PDFs en cada inicio
- **Actualización**: Ejecutar `./update_docs.sh` cuando se agreguen nuevos documentos

**Ventajas de la versión online:**
- ✅ Inicio en segundos (vs minutos)
- ✅ Menor uso de memoria
- ✅ Sin límites de archivos grandes
- ✅ Todos los documentos técnicos disponibles
- ✅ Información de compatibilidad completa

### Actualizar Documentos
```bash
# Agregar nuevos PDFs a docs/manuals/
# Luego ejecutar:
./update_docs.sh

# El script generará docs/rag_documents.json actualizado
# Hacer commit del JSON al repositorio
```

## 🚦 Estados del Lead

```
NEW → COLLECTING_TECH_DATA → QUALIFIED → ASSIGNED
         ↓                        ↓
    FOLLOW_UP ←──────────────────┘
```

### Checkpoints

1. **Lead Recibido**: Canal identificado, mensaje inicial capturado
2. **Datos Técnicos Mínimos**: Nombre, zona, marca, implemento
3. **Lead Calificado**: Score asignado, validación RAG
4. **Asignación de Vendedor**: Vendedor zonal asignado
5. **Preparación CRM**: Sincronizado con Pilot

## 📦 Instalación

### Requisitos

- Python 3.10+
- PostgreSQL (opcional, para persistencia)
- Cuenta de Pilot CRM
- API key de proveedor LLM (OpenRouter/Anthropic)

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-empresa/vp-ai.git
cd vp-ai
```

2. **Crear entorno virtual**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Ejecutar ejemplo**
```bash
cd src
python main.py
```

## 🔧 Configuración

### Variables de Entorno Críticas

```env
# Pilot CRM
PILOT_API_KEY=your_pilot_api_key
PILOT_API_URL=https://api.pilot.com/v1

# LLM (desarrollo con Llama 3.1 8B)
OPENROUTER_API_KEY=your_key
MODEL_PROVIDER=llama

# LLM (producción con Claude 4.5)
ANTHROPIC_API_KEY=your_key
MODEL_PROVIDER=claude

# Vector DB (RAG)
VECTOR_DB_URL=your_pinecone_url
PINECONE_API_KEY=your_key
```

Ver [.env.example](.env.example) para configuración completa.

## 🎯 Uso Básico

### Procesar un Mensaje

```python
from agent import B2BAgent
from models import Canal

# Inicializar agente
agent = B2BAgent()

# Procesar mensaje
response = agent.process_message(
    message="Hola, necesito un balde para una Bobcat S70",
    canal=Canal.WHATSAPP
)

print(response['reply_to_user'])
# "Perfecto, el balde para la Bobcat S70. ¿Lo usarías principalmente en obra, campo o para trabajo industrial?"
```

### Respuesta JSON Estructurada

```json
{
  "reply_to_user": "Perfecto, el balde para la Bobcat S70...",
  "extracted_data": {
    "nombre": null,
    "zona": null,
    "mini_cargadora": {
      "marca": "Bobcat",
      "modelo": "S70",
      "uso": null
    },
    "implemento_interes": "balde",
    "urgencia": null
  },
  "state_transition": "COLLECTING_TECH_DATA",
  "checkpoint": 2,
  "actions": ["search_rag"],
  "lead_score": null,
  "flags": [],
  "next_questions": ["¿En qué zona estás ubicado?"]
}
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html

# Test específico
pytest tests/test_agent.py::TestB2BAgent::test_extract_implemento
```

## 🔌 Integraciones

### Sistema RAG

Valida compatibilidad técnica consultando base de conocimiento vectorial:

```python
from rag_system import get_rag_system

rag = get_rag_system()
result = rag.validate_compatibility(
    implemento="martillo hidráulico",
    marca="Bobcat",
    modelo="S70"
)
```

### Pilot CRM

Sincroniza leads automáticamente:

```python
from crm_client import get_crm_client

crm = get_crm_client()
result = crm.sync_lead(lead_data)
```

## 📊 Sistema de Scoring

| Score | Criterios | Acción |
|-------|-----------|--------|
| **A** | Datos completos + urgencia alta + zona cubierta | Escalamiento inmediato |
| **B** | Datos parciales + implemento identificado | 1-2 interacciones más |
| **C** | Consulta exploratoria | Bajo seguimiento |

## 🛠️ Desarrollo

### Agregar Nuevo Implemento

Editar en [agent.py](src/agent.py):

```python
self.implementos_conocidos = {
    "nuevo_implemento": ["keyword1", "keyword2"],
    # ...
}
```

### Agregar Nueva Marca

```python
self.marcas_conocidas = [
    "nueva_marca",
    # ...
]
```

### Personalizar Respuestas

Editar método `_generate_reply()` en [agent.py](src/agent.py)

## 🚀 Despliegue

### Opción 1: Docker

```bash
docker build -t vp-ai-agent .
docker run -p 8000:8000 --env-file .env vp-ai-agent
```

### Opción 2: Cloud (Render/Railway)

1. Configurar variables de entorno en panel
2. Conectar repositorio GitHub
3. Deploy automático

## 🔐 Seguridad

- ✅ Variables de entorno para credenciales
- ✅ Validación de entrada con Pydantic
- ✅ Rate limiting (implementar en producción)
- ✅ Logging de errores con Sentry

## 📚 Documentación Adicional

- [Prompt del Sistema Completo](prompts/system_prompt.md)
- [Especificación de Estados](docs/states.md) *(crear)*
- [Guía de Integración CRM](docs/crm_integration.md) *(crear)*

## 🐛 Troubleshooting

### Error: "API key not configured"
Verifica que `.env` existe y contiene `PILOT_API_KEY` válido.

### Error: "Invalid state transition"
Revisa que la transición esté permitida en [state_machine.py](src/state_machine.py)

### Respuestas inconsistentes
Ajusta `temperature` en `config.yaml` (reducir para más consistencia)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Propietario - Empresa Metalúrgica © 2025

## 📞 Contacto

- **Equipo de Desarrollo**: dev@empresa.com
- **Soporte Técnico**: soporte@empresa.com

---

## 🎯 Roadmap

- [ ] Integración con WhatsApp Business API
- [ ] Dashboard de analytics en tiempo real
- [ ] Sistema de recomendación de implementos
- [ ] Soporte multiidioma
- [ ] A/B testing de respuestas
- [ ] Migración completa a Claude 4.5 Sonnet

## 📈 Métricas de Rendimiento

| Modelo | Consistencia JSON | Calidad ES | Latencia |
|--------|-------------------|------------|----------|
| Llama 3.1 8B | 85% | 7.5/10 | ~200ms |
| Claude 4.5 | 95% | 9.5/10 | ~400ms |

**Recomendación**: Usar Llama para desarrollo, Claude para producción.

---

**Versión**: 2.1-unificado  
**Última actualización**: Diciembre 2025
