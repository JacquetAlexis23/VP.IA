"""
Modelos de datos para el Asesor Técnico
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AdvisorState(str, Enum):
    """Estados posibles en la máquina de estados del asesor"""
    RECEIVE_QUERY = "RECEIVE_QUERY"
    SEARCH_RAG = "SEARCH_RAG"
    PROVIDE_ADVICE = "PROVIDE_ADVICE"

class Confidence(str, Enum):
    """Nivel de confianza en la respuesta"""
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"

class RAGResult(BaseModel):
    """Resultado de búsqueda RAG"""
    document_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TechnicalResponse(BaseModel):
    """Respuesta del asesor técnico"""
    technical_response: str
    rag_results: List[RAGResult] = Field(default_factory=list)
    state_transition: AdvisorState
    actions: List[str] = Field(default_factory=list)
    confidence: Confidence

    class Config:
        use_enum_values = True

class ErrorResponse(BaseModel):
    """Respuesta de error"""
    error: str
    reason: str