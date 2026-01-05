"""
Máquina de estados para el flujo del agente comercial
"""
from typing import Dict, List, Callable, Optional
from models import LeadState, LeadData, Flag


class StateMachine:
    """
    Máquina de estados para gestionar las transiciones del lead.
    """
    
    # Definir transiciones válidas
    VALID_TRANSITIONS: Dict[LeadState, List[LeadState]] = {
        LeadState.NEW: [
            LeadState.COLLECTING_TECH_DATA,
            LeadState.FOLLOW_UP
        ],
        LeadState.COLLECTING_TECH_DATA: [
            LeadState.QUALIFIED,
            LeadState.FOLLOW_UP,
            LeadState.NEW  # Puede volver si hay confusión
        ],
        LeadState.QUALIFIED: [
            LeadState.ASSIGNED,
            LeadState.FOLLOW_UP
        ],
        LeadState.FOLLOW_UP: [
            LeadState.COLLECTING_TECH_DATA,
            LeadState.QUALIFIED,
            LeadState.ASSIGNED
        ],
        LeadState.ASSIGNED: [
            LeadState.FOLLOW_UP  # Solo si necesita re-seguimiento
        ]
    }
    
    def __init__(self, lead: LeadData):
        self.lead = lead
        self.state_handlers: Dict[LeadState, Callable] = {
            LeadState.NEW: self._handle_new,
            LeadState.COLLECTING_TECH_DATA: self._handle_collecting,
            LeadState.QUALIFIED: self._handle_qualified,
            LeadState.FOLLOW_UP: self._handle_follow_up,
            LeadState.ASSIGNED: self._handle_assigned
        }
    
    def can_transition(self, from_state: LeadState, to_state: LeadState) -> bool:
        """Verifica si una transición de estado es válida"""
        return to_state in self.VALID_TRANSITIONS.get(from_state, [])
    
    def transition(self, new_state: LeadState, checkpoint: int) -> bool:
        """
        Intenta realizar una transición de estado.
        Retorna True si fue exitosa, False si es inválida.
        """
        current_state = self.lead.current_state
        
        if not self.can_transition(current_state, new_state):
            print(f"⚠️ Transición inválida: {current_state} -> {new_state}")
            return False
        
        # Ejecutar handler del estado actual antes de salir
        if current_state in self.state_handlers:
            self.state_handlers[current_state]()
        
        # Realizar la transición
        self.lead.update_state(new_state, checkpoint)
        print(f"✅ Transición exitosa: {current_state} -> {new_state} (Checkpoint {checkpoint})")
        
        return True
    
    def get_required_data_for_state(self, state: LeadState) -> List[str]:
        """Retorna los datos requeridos para alcanzar un estado específico"""
        requirements = {
            LeadState.NEW: [],
            LeadState.COLLECTING_TECH_DATA: [
                "implemento_interes"
            ],
            LeadState.QUALIFIED: [
                "nombre",
                "zona",
                "marca",
                "implemento_interes"
            ],
            LeadState.ASSIGNED: [
                "nombre",
                "zona",
                "marca",
                "implemento_interes",
                "vendedor_asignado"
            ],
            LeadState.FOLLOW_UP: []  # Flexible
        }
        return requirements.get(state, [])
    
    def _handle_new(self):
        """Handler para estado NEW"""
        # Primer contacto, validar canal
        if not self.lead.canal:
            print("⚠️ Canal no identificado en estado NEW")
    
    def _handle_collecting(self):
        """Handler para estado COLLECTING_TECH_DATA"""
        # Verificar si tenemos datos mínimos
        missing = self.lead.get_missing_data()
        if missing:
            self.lead.add_flag(Flag.MISSING_TECH_DATA)
        else:
            self.lead.remove_flag(Flag.MISSING_TECH_DATA)
    
    def _handle_qualified(self):
        """Handler para estado QUALIFIED"""
        # Validar que el lead esté completamente calificado
        if not self.lead.is_qualified():
            print("⚠️ Lead en estado QUALIFIED pero le faltan datos")
            self.lead.add_flag(Flag.MISSING_TECH_DATA)
    
    def _handle_follow_up(self):
        """Handler para estado FOLLOW_UP"""
        # Identificar qué datos faltan para follow-up efectivo
        missing = self.lead.get_missing_data()
        if missing:
            print(f"📋 Datos faltantes para follow-up: {', '.join(missing)}")
    
    def _handle_assigned(self):
        """Handler para estado ASSIGNED"""
        # Verificar que haya vendedor asignado
        if not self.lead.assigned_vendor:
            print("⚠️ Lead en estado ASSIGNED sin vendedor asignado")
    
    def suggest_next_state(self) -> Optional[LeadState]:
        """
        Sugiere el próximo estado lógico basado en los datos actuales.
        """
        current = self.lead.current_state
        
        if current == LeadState.NEW:
            # Si hay implemento de interés, pasar a recolección
            if self.lead.extracted_data.implemento_interes:
                return LeadState.COLLECTING_TECH_DATA
            return None
        
        elif current == LeadState.COLLECTING_TECH_DATA:
            # Si está calificado, avanzar
            if self.lead.is_qualified():
                return LeadState.QUALIFIED
            # Si faltan muchos datos, follow-up
            missing = self.lead.get_missing_data()
            if len(missing) > 2:
                return LeadState.FOLLOW_UP
            return None
        
        elif current == LeadState.QUALIFIED:
            # Si está calificado y tiene zona, asignar
            if self.lead.extracted_data.zona:
                return LeadState.ASSIGNED
            return None
        
        elif current == LeadState.FOLLOW_UP:
            # Si completó datos, volver a collecting
            if self.lead.is_qualified():
                return LeadState.QUALIFIED
            elif self.lead.extracted_data.implemento_interes:
                return LeadState.COLLECTING_TECH_DATA
            return None
        
        elif current == LeadState.ASSIGNED:
            # Estado final generalmente
            return None
        
        return None
    
    def get_checkpoint_for_state(self, state: LeadState) -> int:
        """Retorna el checkpoint correspondiente a un estado"""
        checkpoint_map = {
            LeadState.NEW: 1,
            LeadState.COLLECTING_TECH_DATA: 2,
            LeadState.QUALIFIED: 3,
            LeadState.ASSIGNED: 4,
            LeadState.FOLLOW_UP: 2  # Varía según contexto
        }
        return checkpoint_map.get(state, 1)
