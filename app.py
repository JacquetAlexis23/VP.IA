"""
Interfaz gráfica para probar el Asesor Técnico
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import json
from agent import TechnicalAdvisor

# Configuración de la página
st.set_page_config(
    page_title="Asesor Técnico para Vendedores",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar elementos de Streamlit para interfaz más limpia
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🔧 Asesor Técnico para Vendedores")
st.markdown("**Consulta información técnica de implementos para mini cargadoras**")

# Información del sistema
with st.sidebar:
    st.header("ℹ️ Información del Sistema")
    st.markdown("""
    **Estado:** Online 🟢

    **Documentos cargados:** 44 PDFs técnicos

    **Modelos soportados:** CVM, BAR, TH, etc.

    **Versión:** 2.1-unificado
    """)

    if st.button("🔄 Recargar Base de Conocimiento"):
        st.cache_data.clear()
        st.rerun()

# Inicializar asesor en session_state con cache
@st.cache_resource
def get_advisor():
    return TechnicalAdvisor(system_prompt_path="prompts/system_prompt.md")

if 'advisor' not in st.session_state:
    st.session_state.advisor = get_advisor()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Función para procesar consulta
def process_query(query):
    """Procesa una consulta técnica"""
    try:
        response = st.session_state.advisor.process_query(query)
        print(f"Respuesta del agente: {response}")
        
        # Agregar al historial de UI
        st.session_state.chat_history.append({
            "role": "user",
            "message": query,
            "timestamp": "Ahora"
        })

        technical_response = response.get("technical_response", "Error en respuesta")
        print(f"Respuesta técnica: {technical_response}")
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "message": technical_response,
            "timestamp": "Ahora"
        })

        return response
    except Exception as e:
        print(f"Error procesando consulta: {e}")
        st.session_state.chat_history.append({
            "role": "user",
            "message": query,
            "timestamp": "Ahora"
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "message": f"Error: {str(e)}",
            "timestamp": "Ahora"
        })
        return {"error": str(e)}

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Consultas Técnicas")

    # Mostrar historial de chat
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"**👤 Vendedor:** {msg['message']}")
            else:
                st.markdown(f"**🔧 Asesor:** {msg['message']}")
            st.markdown("---")

    # Input para nueva consulta
    with st.form("query_form"):
        user_query = st.text_input("Escribe tu consulta técnica:", placeholder="Ej: ¿Cuáles son las especificaciones del balde para Bobcat S70?")

        submitted = st.form_submit_button("Enviar consulta")
        if submitted and user_query.strip():
            response = process_query(user_query.strip())
            st.rerun()

with col2:
    st.subheader("📚 Información Técnica")

    st.markdown("**Estado actual:**")
    state_display = str(st.session_state.advisor.current_state).split('.')[-1]
    st.info(f"{state_display}")

    st.markdown("**Documentos cargados:**")
    if hasattr(st.session_state.advisor.rag_system, 'documents'):
        st.metric("Fichas técnicas", len(st.session_state.advisor.rag_system.documents))

        # Mostrar tipos de documentos
        st.markdown("**Tipos de documentos:**")
        doc_types = {}
        for doc in st.session_state.advisor.rag_system.documents:
            doc_type = doc.metadata.get('categoria', 'general')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        for doc_type, count in doc_types.items():
            st.info(f"{doc_type.title()}: {count} documentos")

        # Estado de confianza
        st.markdown("**Última consulta:**")
        if 'last_response' in st.session_state and st.session_state.last_response:
            confidence = st.session_state.last_response.get('confidence', 'N/A')
            confidence_colors = {
                'ALTA': '🟢',
                'MEDIA': '🟡', 
                'BAJA': '🔴'
            }
            st.success(f"Confianza: {confidence_colors.get(str(confidence).upper(), '⚪')} {confidence}")
        else:
            st.info("Aún no hay consultas procesadas")

    else:
        st.info("No hay lead activo. Envía un mensaje para comenzar.")

    # Botones de control
    st.markdown("---")
    if st.button("🗑️ Reiniciar conversación"):
        st.session_state.lead = None
        st.session_state.chat_history = []
        st.rerun()

    if st.button("📋 Ver ejemplos de mensajes"):
        st.markdown("""
        **Ejemplos de mensajes para probar:**

        1. "Hola, necesito un balde para una Bobcat S70"
        2. "Lo usaría principalmente en obra"
        3. "Estoy en Buenos Aires, soy Juan"
        4. "Busco un martillo hidráulico para Caterpillar 242D"
        5. "Trabajo en campo agrícola"
        """)

# Footer
st.markdown("---")
st.markdown("*Interfaz de prueba - Agente B2B con IA generativa*")