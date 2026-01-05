"""
Punto de entrada principal del agente
"""
import os
import json
from dotenv import load_dotenv
from agent import B2BAgent
from models import Canal, LeadData


def main():
    """Función principal para testing del agente"""
    # Cargar variables de entorno
    load_dotenv()
    
    # Inicializar agente
    print("🚀 Inicializando Agente Comercial Técnico B2B\n")
    agent = B2BAgent()
    
    # Ejemplo de conversación simulada
    print("=" * 60)
    print("EJEMPLO DE CONVERSACIÓN")
    print("=" * 60)
    
    # Lead tracking
    lead = None
    
    # Mensaje 1: Contacto inicial
    print("\n👤 Usuario: Hola, necesito un balde para una Bobcat S70")
    response1 = agent.process_message(
        "Hola, necesito un balde para una Bobcat S70",
        lead=lead,
        canal=Canal.WHATSAPP
    )
    print(f"🤖 Agente: {response1['reply_to_user']}")
    print(f"📊 Estado: {response1['state_transition']} | Checkpoint: {response1['checkpoint']}")
    print(f"📋 JSON completo:\n{json.dumps(response1, indent=2, ensure_ascii=False)}\n")
    
    # Crear lead con datos extraídos
    lead = LeadData(
        canal=Canal.WHATSAPP,
        mensaje_inicial="Hola, necesito un balde para una Bobcat S70"
    )
    lead.extracted_data.implemento_interes = response1['extracted_data'].get('implemento_interes')
    lead.extracted_data.mini_cargadora.marca = response1['extracted_data']['mini_cargadora'].get('marca')
    lead.extracted_data.mini_cargadora.modelo = response1['extracted_data']['mini_cargadora'].get('modelo')
    
    # Mensaje 2: Responder uso
    print("👤 Usuario: Lo usaría principalmente en obra")
    response2 = agent.process_message(
        "Lo usaría principalmente en obra",
        lead=lead
    )
    print(f"🤖 Agente: {response2['reply_to_user']}")
    print(f"📊 Estado: {response2['state_transition']} | Checkpoint: {response2['checkpoint']}")
    print(f"📋 JSON:\n{json.dumps(response2, indent=2, ensure_ascii=False)}\n")
    
    # Mensaje 3: Agregar zona
    print("👤 Usuario: Estoy en Buenos Aires, soy Juan")
    response3 = agent.process_message(
        "Estoy en Buenos Aires, soy Juan",
        lead=lead
    )
    print(f"🤖 Agente: {response3['reply_to_user']}")
    print(f"📊 Estado: {response3['state_transition']} | Checkpoint: {response3['checkpoint']}")
    print(f"🎯 Lead Score: {response3.get('lead_score')}")
    print(f"📋 JSON:\n{json.dumps(response3, indent=2, ensure_ascii=False)}\n")
    
    print("=" * 60)
    print("✅ Ejemplo completado")
    print("=" * 60)


if __name__ == "__main__":
    main()
