# Guía de Inicio Rápido - Agente Comercial B2B

## ⚡ Inicio en 5 minutos

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

Mínimo requerido:
```env
PILOT_API_KEY=tu_api_key
MODEL_PROVIDER=llama  # o claude
```

### 3. Ejecutar Ejemplo
```bash
cd src
python main.py
```

## 📝 Ejemplo de Uso

```python
from agent import B2BAgent
from models import Canal

agent = B2BAgent()

# Primera interacción
response = agent.process_message(
    "Hola, necesito un balde para una Bobcat S70",
    canal=Canal.WHATSAPP
)

print(response['reply_to_user'])
print(f"Estado: {response['state_transition']}")
print(f"Score: {response.get('lead_score')}")
```

## 🧪 Ejecutar Tests

```bash
pytest tests/ -v
```

## 📚 Próximos Pasos

1. Lee el [README.md](../README.md) completo
2. Revisa el [prompt del sistema](../prompts/system_prompt.md)
3. Explora los [tests](../tests/test_agent.py) para ejemplos
4. Configura integraciones RAG y CRM

## 🆘 Ayuda

- Errores comunes: ver sección Troubleshooting en README
- Documentación API: ver docstrings en código
- Contacto: dev@empresa.com
