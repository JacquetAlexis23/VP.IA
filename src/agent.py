"""
Asesor Técnico para Vendedores
"""
import json
import sys
import os
sys.path.append(os.path.dirname(__file__))

from typing import Dict, Any, Optional, List
from models import (
    AdvisorState, TechnicalResponse, RAGResult, Confidence,
    ErrorResponse
)
from llm_client import LLMClient
from rag_system import RAGSystem, RAGDocument


class TechnicalAdvisor:
    """
    Asesor técnico que proporciona información de fichas técnicas a vendedores.
    """

    def __init__(self, system_prompt_path: str = "prompts/system_prompt.md"):
        """Inicializa el asesor con el prompt del sistema"""
        self.system_prompt = self._load_system_prompt(system_prompt_path)

        # Inicializar cliente LLM
        self.llm_client = LLMClient(model_name="xiaomi/mimo-v2-flash:free")

        # Inicializar sistema RAG
        self.rag_system = RAGSystem()

        # Estado actual
        self.current_state = AdvisorState.RECEIVE_QUERY

    def _load_system_prompt(self, path: str) -> str:
        """Carga el prompt del sistema desde archivo"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ No se encontró el prompt del sistema en {path}")
            return ""

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Procesa una consulta técnica del vendedor.

        Args:
            query: Consulta del vendedor

        Returns:
            Dict con la respuesta técnica en formato JSON
        """
        try:
            print(f"🔍 Procesando consulta: {query}")

            # Cambiar estado a SEARCH_RAG
            self.current_state = AdvisorState.SEARCH_RAG

            # Buscar en RAG
            rag_results = self.rag_system.search(query)
            print(f"📚 Encontrados {len(rag_results)} resultados RAG")

            # Generar respuesta usando LLM
            response = self._generate_technical_response(query, rag_results)
            print(f"🤖 Respuesta generada: {response}")

            # Cambiar estado a PROVIDE_ADVICE
            self.current_state = AdvisorState.PROVIDE_ADVICE

            # Retornar respuesta
            final_response = response.dict(exclude_none=True)
            print(f"📤 Respuesta final: {final_response}")
            return final_response

        except Exception as e:
            print(f"❌ Error procesando consulta: {str(e)}")
            import traceback
            traceback.print_exc()
            error_response = ErrorResponse(
                error="No se pudo procesar la consulta",
                reason=str(e)
            )
            return error_response.dict()

    def _generate_technical_response(self, query: str, rag_results: List[RAGDocument]) -> TechnicalResponse:
        """Genera respuesta técnica usando LLM"""

        # Preparar contexto RAG
        rag_context = ""
        rag_list = []
        for result in rag_results[:3]:  # Top 3 results
            rag_context += f"Documento: {result.id}\n{result.content}\n\n"
            rag_list.append(RAGResult(
                document_id=result.id,
                content=result.content[:200] + "...",  # Truncar para respuesta
                metadata=result.metadata
            ))

        # Prompt para LLM
        user_prompt = f"""
Consulta del vendedor: {query}

Resultados RAG disponibles:
{rag_context}

Proporciona una respuesta técnica detallada basada únicamente en la información de las fichas técnicas.
"""

        # Llamar a LLM
        llm_response = self.llm_client.generate_with_context(
            system_prompt=self.system_prompt,
            user_message=user_prompt
        )

        # Parsear JSON de la respuesta
        try:
            response_data = json.loads(llm_response)
            return TechnicalResponse(**response_data)
        except Exception as e:
            print(f"❌ Error parseando JSON: {e}")
            # Fallback si no es JSON válido
            return TechnicalResponse(
                technical_response="Lo siento, no pude procesar la información correctamente. Consulta con el departamento técnico.",
                rag_results=rag_list,
                state_transition=AdvisorState.PROVIDE_ADVICE,
                actions=[],
                confidence=Confidence.BAJA
            )
