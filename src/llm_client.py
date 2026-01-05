"""
Cliente LLM para integración con modelos locales o APIs
"""
import os
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde el directorio padre
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


class LLMClient:
    """
    Cliente para modelos LLM vía API (OpenRouter) o local
    """

    def __init__(self, use_api: bool = True, model_name: str = "xiaomi/mimo-v2-flash:free"):
        """
        Inicializa el cliente LLM

        Args:
            use_api: Si usar API (OpenRouter) o local
            model_name: Nombre del modelo
        """
        self.use_api = use_api
        self.model_name = model_name
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # Para local (fallback)
        self.tokenizer = None
        self.model = None
        self.pipe = None

    def load_model(self):
        """Carga el modelo local (solo si es necesario)"""
        if self.model is None:
            print(f"🔄 Cargando modelo local {self.model_name}...")
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
                import torch

                token = os.getenv("HF_TOKEN")
                if not token and "llama" in self.model_name.lower():
                    print("⚠️  HF_TOKEN no encontrado, modelo local limitado")
                    return False

                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, token=token)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name, token=token,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    low_cpu_mem_usage=True
                )

                self.pipe = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

                print("✅ Modelo local cargado")
                return True

            except Exception as e:
                print(f"❌ Error cargando modelo local: {e}")
                return False

        return True

    def generate(self, prompt: str, max_tokens: int = 200) -> Optional[str]:
        """
        Genera respuesta del modelo

        Args:
            prompt: Prompt de entrada
            max_tokens: Máximo tokens a generar

        Returns:
            Respuesta generada o None si error
        """
        # Intentar API primero
        if self.use_api and self.api_key:
            return self._generate_api(prompt, max_tokens)

        # Fallback a local
        return self._generate_local(prompt, max_tokens)

    def _generate_api(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Genera usando OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }

            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print(f"❌ Error API: {e}")
            return None

    def _generate_local(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Genera usando modelo local (fallback)"""
        if not self.load_model():
            return None

        try:
            outputs = self.pipe(
                prompt,
                max_new_tokens=max_tokens,
                num_return_sequences=1,
                return_full_text=False
            )
            return outputs[0]['generated_text'].strip()
        except Exception as e:
            print(f"❌ Error local: {e}")
            return None

    def generate_with_context(self, system_prompt: str, user_message: str, context: str = "") -> Optional[str]:
        """
        Genera respuesta con contexto de sistema y usuario
        """
        if self.use_api:
            # Para API, usar formato de chat
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_message}\n\n{context}" if context else user_message}
            ]
            return self._generate_api_chat(messages)
        else:
            # Para local, usar formato de texto
            prompt = f"System: {system_prompt}\n\nUser: {user_message}"
            if context:
                prompt += f"\n\nContext: {context}"
            prompt += "\n\nAssistant:"
            return self.generate(prompt)

    def _generate_api_chat(self, messages: list, max_tokens: int = 800) -> Optional[str]:
        """Genera usando OpenRouter API con formato chat"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }

            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Limpiar posibles bloques de código markdown
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return content

        except Exception as e:
            print(f"❌ Error API chat: {e}")
            return None