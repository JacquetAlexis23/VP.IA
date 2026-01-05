"""
Integración con CRM Pilot para sincronización de leads
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from models import LeadData, Canal
import requests


class PilotCRMClient:
    """
    Cliente para sincronización con Pilot CRM.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa el cliente de CRM.
        
        Args:
            api_key: API key de Pilot CRM
            api_url: URL base del API de Pilot
        """
        self.api_key = api_key or os.getenv("PILOT_API_KEY")
        self.api_url = api_url or os.getenv("PILOT_API_URL", "https://api.pilot.com/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_lead(self, lead: LeadData) -> Dict[str, Any]:
        """
        Crea un nuevo lead en Pilot CRM.
        
        Args:
            lead: Datos del lead a sincronizar
            
        Returns:
            Dict con respuesta del CRM (incluyendo ID asignado)
        """
        if not self.api_key:
            print("⚠️ API key de Pilot no configurada")
            return {"success": False, "error": "API key not configured"}
        
        payload = self._prepare_lead_payload(lead)
        
        try:
            response = requests.post(
                f"{self.api_url}/leads",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Lead creado en Pilot CRM: {result.get('id')}")
            return {
                "success": True,
                "crm_id": result.get("id"),
                "data": result
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al crear lead en Pilot: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_lead(self, crm_id: str, lead: LeadData) -> Dict[str, Any]:
        """
        Actualiza un lead existente en Pilot CRM.
        
        Args:
            crm_id: ID del lead en el CRM
            lead: Datos actualizados del lead
            
        Returns:
            Dict con respuesta del CRM
        """
        if not self.api_key:
            return {"success": False, "error": "API key not configured"}
        
        payload = self._prepare_lead_payload(lead)
        
        try:
            response = requests.put(
                f"{self.api_url}/leads/{crm_id}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Lead actualizado en Pilot CRM: {crm_id}")
            return {
                "success": True,
                "crm_id": crm_id,
                "data": result
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al actualizar lead en Pilot: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def assign_to_vendor(
        self,
        crm_id: str,
        vendor_id: str,
        zona: str
    ) -> Dict[str, Any]:
        """
        Asigna un lead a un vendedor en el CRM.
        
        Args:
            crm_id: ID del lead en el CRM
            vendor_id: ID del vendedor
            zona: Zona geográfica
            
        Returns:
            Dict con respuesta del CRM
        """
        if not self.api_key:
            return {"success": False, "error": "API key not configured"}
        
        payload = {
            "assigned_to": vendor_id,
            "zone": zona,
            "assigned_at": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/leads/{crm_id}/assign",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Lead asignado a vendedor {vendor_id}")
            return {
                "success": True,
                "vendor_id": vendor_id,
                "data": result
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al asignar lead: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_vendor_by_zone(self, zona: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el vendedor asignado a una zona geográfica.
        
        Args:
            zona: Zona geográfica
            
        Returns:
            Dict con información del vendedor o None
        """
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/vendors",
                headers=self.headers,
                params={"zone": zona},
                timeout=10
            )
            response.raise_for_status()
            vendors = response.json()
            
            if vendors:
                return vendors[0]  # Retornar primer vendedor de la zona
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener vendedor: {str(e)}")
            return None
    
    def _prepare_lead_payload(self, lead: LeadData) -> Dict[str, Any]:
        """Prepara el payload para enviar al CRM"""
        payload = {
            "source": lead.canal.value if lead.canal else "unknown",
            "created_at": lead.timestamp.isoformat(),
            "state": lead.current_state.value,
            "score": lead.lead_score.value if lead.lead_score else None,
            "contact": {
                "name": lead.extracted_data.nombre,
                "zone": lead.extracted_data.zona
            },
            "technical_data": {
                "machine_brand": lead.extracted_data.mini_cargadora.marca,
                "machine_model": lead.extracted_data.mini_cargadora.modelo,
                "machine_use": lead.extracted_data.mini_cargadora.uso.value if lead.extracted_data.mini_cargadora.uso else None,
                "implement_interest": lead.extracted_data.implemento_interes,
                "urgency": lead.extracted_data.urgencia.value if lead.extracted_data.urgencia else None
            },
            "conversation_history": lead.conversation_history,
            "flags": [flag.value for flag in lead.flags],
            "checkpoint": lead.checkpoint
        }
        
        return payload
    
    def sync_lead(self, lead: LeadData) -> Dict[str, Any]:
        """
        Sincroniza un lead con el CRM (crea o actualiza).
        
        Args:
            lead: Lead a sincronizar
            
        Returns:
            Dict con resultado de la sincronización
        """
        if lead.crm_id:
            # Lead ya existe, actualizar
            result = self.update_lead(lead.crm_id, lead)
        else:
            # Lead nuevo, crear
            result = self.create_lead(lead)
            
            # Guardar CRM ID si fue exitoso
            if result.get("success"):
                lead.crm_id = result.get("crm_id")
                lead.synced_to_crm = True
        
        return result


# Singleton para uso global
_crm_instance: Optional[PilotCRMClient] = None


def get_crm_client() -> PilotCRMClient:
    """Retorna la instancia singleton del cliente CRM"""
    global _crm_instance
    if _crm_instance is None:
        _crm_instance = PilotCRMClient()
    return _crm_instance
