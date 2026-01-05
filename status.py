# Archivo de estado para monitoreo
# Este archivo se actualiza cada vez que se inicia la aplicación

import json
import os
from datetime import datetime

status = {
    "status": "online",
    "version": "2.1-unificado",
    "last_startup": datetime.now().isoformat(),
    "environment": os.getenv("STREAMLIT_SERVER_HEADLESS", "development"),
    "documents_loaded": 44,
    "supported_models": ["CVM120", "BAR150", "TH300", "H900", "HD400", "HR260", "MX400", "PN210", "PNA210", "RA600", "RP270", "RS220", "RV150", "Z1200"]
}

# Guardar estado
with open("status.json", "w") as f:
    json.dump(status, f, indent=2)

print("✅ Status actualizado:", status["last_startup"])