"""
Sistema RAG (Retrieval-Augmented Generation) para validación técnica
"""
import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from pypdf import PdfReader
from PIL import Image
import pytesseract
import io


@dataclass
class RAGDocument:
    """Documento en la base de conocimiento RAG"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class RAGSystem:
    """
    Sistema de recuperación de información técnica.
    Valida compatibilidad de implementos con mini cargadoras.
    """
    
    def __init__(self, vector_db_url: Optional[str] = None):
        """
        Inicializa el sistema RAG.
        
        Args:
            vector_db_url: URL de la base de datos vectorial (ej: Pinecone, Weaviate)
        """
        self.vector_db_url = vector_db_url or os.getenv("VECTOR_DB_URL")
        self.documents: List[RAGDocument] = []
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Carga la base de conocimiento técnico desde JSON o PDFs"""
        docs_path = Path(__file__).parent.parent / "docs"
        
        # PRIMERO: Intentar cargar desde JSON preprocesado (para producción)
        json_path = docs_path / "rag_documents.json"
        if json_path.exists():
            try:
                self._load_from_json(json_path)
                if self.documents:
                    print(f"✅ Base de conocimiento cargada desde JSON: {len(self.documents)} documentos")
                    return  # Si cargó correctamente, no procesar PDFs
            except Exception as e:
                print(f"⚠️ Error cargando JSON, intentando con PDFs: {e}")
        
        # SEGUNDO: Cargar desde PDFs si no hay JSON o falló
        print("🔄 Procesando documentos desde archivos...")
        
        # Cargar PDFs de la carpeta docs/
        pdf_files = list(docs_path.glob("*.pdf"))
        if pdf_files:
            self._load_from_pdfs(pdf_files)
        
        # Cargar PDFs de la carpeta manuals/
        manuals_path = docs_path / "manuals"
        if manuals_path.exists():
            manuals_pdf_files = list(manuals_path.glob("*.pdf"))
            if manuals_pdf_files:
                self._load_from_pdfs(manuals_pdf_files)
        
        # Cargar archivos de texto como respaldo
        txt_files = list(docs_path.glob("*.txt"))
        if txt_files:
            self._load_from_txts(txt_files)
        
        # Cargar archivos de texto de manuals/
        if manuals_path.exists():
            manuals_txt_files = list(manuals_path.glob("*.txt"))
            if manuals_txt_files:
                self._load_from_txts(manuals_txt_files)
        
        # Fallback a datos de ejemplo si no hay nada
        if not self.documents:
            self._load_example_data()
    
    def _load_from_json(self, file_path: Path):
        """Carga documentos desde archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.documents = []
            for doc_data in data.get('documents', []):
                doc = RAGDocument(
                    id=doc_data['id'],
                    content=doc_data['content'],
                    metadata=doc_data.get('metadata', {})
                )
                self.documents.append(doc)
                
            print(f"✅ Cargados {len(self.documents)} documentos desde {file_path}")
            
        except Exception as e:
            print(f"❌ Error cargando documentos: {e}")
            self._load_example_data()
    
    def _load_from_pdfs(self, pdf_files: List[Path]):
        """Carga documentos desde archivos PDF"""
        for pdf_path in pdf_files:
            try:
                print(f"🔄 Procesando PDF: {pdf_path.name}")
                reader = PdfReader(pdf_path)
                
                # Limitar a las primeras 20 páginas para rendimiento en la nube
                max_pages = min(20, len(reader.pages))
                content = ""
                
                for i, page in enumerate(reader.pages[:max_pages]):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():  # Solo agregar si hay contenido
                            content += page_text + "\n"
                    except Exception as e:
                        print(f"⚠️ Error en página {i+1} de {pdf_path.name}: {e}")
                        continue
                
                # Solo intentar OCR si está explícitamente habilitado (deshabilitado por defecto en nube)
                use_ocr = os.getenv("ENABLE_OCR", "false").lower() == "true"
                if not content.strip() and use_ocr:
                    print(f"   🔄 Intentando OCR para {pdf_path.name}...")
                    content = self._extract_text_with_ocr(pdf_path, min(max_pages, 5))
                
                if not content.strip():
                    print(f"   ⚠️ No se pudo extraer texto ni con OCR de {pdf_path.name}")
                    continue
                
                # Extraer metadata del nombre del archivo
                filename = pdf_path.stem
                metadata = self._extract_metadata_from_filename(filename)
                
                doc = RAGDocument(
                    id=f"pdf_{filename}",
                    content=content.strip(),
                    metadata=metadata
                )
                self.documents.append(doc)
                print(f"✅ Cargado PDF: {pdf_path.name} ({len(reader.pages)} páginas, {len(content)} caracteres)")
                
            except Exception as e:
                print(f"❌ Error cargando PDF {pdf_path.name}: {e}")
                continue
        
        print(f"✅ Cargados {len(self.documents)} documentos desde PDFs")
    
    def _load_from_txts(self, txt_files: List[Path]):
        """Carga documentos desde archivos de texto"""
        for txt_path in txt_files:
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraer metadata del nombre del archivo
                metadata = self._extract_metadata_from_filename(txt_path.stem)
                
                doc = RAGDocument(
                    id=f"txt_{txt_path.stem}",
                    content=content.strip(),
                    metadata=metadata
                )
                self.documents.append(doc)
                print(f"✅ Cargado TXT: {txt_path.name}")
                
            except Exception as e:
                print(f"❌ Error cargando TXT {txt_path.name}: {e}")
        
        print(f"✅ Cargados {len(self.documents)} documentos desde archivos de texto")
    
    def _extract_text_with_ocr(self, pdf_path: Path, max_pages: int = 10) -> str:
        """Extrae texto de PDF usando OCR (para PDFs con imágenes)"""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            # Configurar Tesseract para español
            custom_config = r'--oem 3 --psm 6 -l spa+eng'
            
            # Convertir PDF a imágenes (primeras páginas)
            images = convert_from_path(pdf_path, first_page=1, last_page=min(max_pages, 10))
            
            text = ""
            for i, image in enumerate(images):
                try:
                    page_text = pytesseract.image_to_string(image, config=custom_config)
                    if page_text.strip():
                        text += page_text + "\n"
                        print(f"   📝 OCR página {i+1}: {len(page_text)} caracteres")
                except Exception as e:
                    print(f"   ⚠️ Error OCR en página {i+1}: {e}")
            
            return text.strip()
            
        except ImportError:
            print("   ⚠️ pdf2image no instalado. Instala con: pip install pdf2image")
            return ""
        except Exception as e:
            print(f"   ❌ Error en OCR: {e}")
            return ""
    
    def _extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """Extrae metadata del nombre del archivo PDF"""
        metadata = {"categoria": "manual_tecnico"}
        
        # Convertir a minúsculas para búsqueda
        filename_lower = filename.lower()
        
        # Buscar marcas conocidas
        marcas = ["bobcat", "caterpillar", "jcb", "case", "john deere", "komatsu", "alkimax"]
        marca_encontrada = None
        for marca in marcas:
            if marca in filename_lower:
                marca_encontrada = marca.title() if marca != "john deere" else "John Deere"
                break
        
        if marca_encontrada:
            metadata["marca"] = marca_encontrada
        
        # Buscar modelos comunes
        modelos = ["s70", "s450", "s650", "sr160", "sr175", "sv185", "531-70", "535-125", "541-70", "242d", "2025r"]
        modelo_encontrado = None
        for modelo in modelos:
            if modelo in filename_lower:
                modelo_encontrado = modelo.upper()
                break
        
        if modelo_encontrado:
            metadata["modelo"] = modelo_encontrado
        
        # Determinar tipo de documento
        if "manual" in filename_lower or "operario" in filename_lower or "owner" in filename_lower:
            metadata["tipo"] = "manual_operacion"
        elif "especificaciones" in filename_lower or "specs" in filename_lower:
            metadata["tipo"] = "especificaciones"
        elif "compatibilidad" in filename_lower:
            metadata["tipo"] = "compatibilidad"
        elif "instrucciones" in filename_lower:
            metadata["tipo"] = "instrucciones"
        else:
            metadata["tipo"] = "manual_tecnico"
        
        return metadata
    
    def _load_example_data(self):
        """Carga datos de ejemplo"""
        self.documents = [
            RAGDocument(
                id="doc_001",
                content="Bobcat S70: Capacidad de carga 320kg, sistema hidráulico 45L/min, compatible con baldes hasta 0.3m³",
                metadata={
                    "marca": "Bobcat",
                    "modelo": "S70",
                    "categoria": "especificaciones"
                }
            ),
            RAGDocument(
                id="doc_002",
                content="Caterpillar 242D: Sistema hidráulico de alta presión, compatible con martillos hasta 500kg",
                metadata={
                    "marca": "Caterpillar",
                    "modelo": "242D",
                    "categoria": "compatibilidad"
                }
            ),
        ]
        print(f"⚠️ Usando datos de ejemplo ({len(self.documents)} documentos)")
    
    def add_document(self, content: str, metadata: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """
        Agrega un nuevo documento a la base de conocimiento
        
        Args:
            content: Contenido del documento
            metadata: Metadata (marca, modelo, categoria, etc.)
            doc_id: ID opcional del documento
            
        Returns:
            ID del documento agregado
        """
        if doc_id is None:
            doc_id = f"doc_{len(self.documents) + 1:03d}"
            
        doc = RAGDocument(
            id=doc_id,
            content=content,
            metadata=metadata
        )
        
        self.documents.append(doc)
        print(f"✅ Documento agregado: {doc_id}")
        return doc_id
    
    def save_documents(self, file_path: Optional[Path] = None):
        """
        Guarda los documentos actuales a archivo JSON
        
        Args:
            file_path: Ruta opcional del archivo
        """
        if file_path is None:
            file_path = Path(__file__).parent.parent / "docs" / "rag_documents.json"
        
        file_path.parent.mkdir(exist_ok=True)
        
        data = {
            "documents": [
                {
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata
                }
                for doc in self.documents
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Documentos guardados en {file_path}")
    
    def load_from_directory(self, directory_path: str, file_pattern: str = "*.txt"):
        """
        Carga documentos desde archivos en un directorio
        
        Args:
            directory_path: Ruta del directorio
            file_pattern: Patrón de archivos (ej: "*.txt", "*.md", "*.pdf")
        """
        dir_path = Path(directory_path)
        if not dir_path.exists():
            print(f"❌ Directorio no encontrado: {directory_path}")
            return
        
        loaded_count = 0
        for file_path in dir_path.glob(file_pattern):
            try:
                content = ""
                metadata = {}
                
                if file_path.suffix.lower() == '.pdf':
                    content, metadata = self._load_pdf_content(file_path)
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                # Extraer metadata del nombre del archivo
                filename_metadata = self._extract_metadata_from_filename(file_path.stem)
                metadata.update(filename_metadata)
                
                if content.strip():  # Solo agregar si hay contenido
                    self.add_document(
                        content=content,
                        metadata=metadata,
                        doc_id=f"file_{file_path.stem}"
                    )
                    loaded_count += 1
                
            except Exception as e:
                print(f"❌ Error cargando {file_path}: {e}")
        
        print(f"✅ Cargados {loaded_count} archivos desde {directory_path}")
    
    def _load_pdf_content(self, file_path: Path) -> tuple[str, Dict[str, Any]]:
        """
        Extrae contenido de un archivo PDF
        
        Returns:
            Tupla de (contenido, metadata)
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            content = ""
            metadata = {"tipo": "pdf", "paginas": len(reader.pages)}
            
            # Extraer texto de todas las páginas
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    content += page_text + "\n\n"
            
            # Metadata del PDF si está disponible
            if reader.metadata:
                if reader.metadata.title:
                    metadata["titulo"] = reader.metadata.title
                if reader.metadata.author:
                    metadata["autor"] = reader.metadata.author
                if reader.metadata.subject:
                    metadata["asunto"] = reader.metadata.subject
            
            return content.strip(), metadata
            
        except ImportError:
            print("❌ PyPDF2 no instalado. Instala con: pip install PyPDF2")
            return "", {}
        except Exception as e:
            print(f"❌ Error procesando PDF {file_path}: {e}")
            return "", {}
    
    def _extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """
        Extrae metadata del nombre del archivo
        Ejemplo: "Bobcat_S70_Especificaciones.txt" -> {"marca": "Bobcat", "modelo": "S70", "categoria": "especificaciones"}
        """
        metadata = {"categoria": "general"}
        
        # Intentar extraer marca y modelo
        parts = filename.replace('_', ' ').split()
        
        # Marcas conocidas
        marcas = ["bobcat", "caterpillar", "cat", "john deere", "case", "new holland", "kubota"]
        for marca in marcas:
            if marca.lower() in filename.lower():
                metadata["marca"] = marca.title()
                break
        
        # Buscar patrón de modelo (letras + números)
        import re
        modelo_match = re.search(r'([A-Za-z]+\d+)', filename)
        if modelo_match:
            metadata["modelo"] = modelo_match.group(1).upper()
        
        # Categorías comunes
        if "especificaciones" in filename.lower() or "specs" in filename.lower():
            metadata["categoria"] = "especificaciones"
        elif "compatibilidad" in filename.lower() or "compatible" in filename.lower():
            metadata["categoria"] = "compatibilidad"
        elif "manual" in filename.lower():
            metadata["categoria"] = "manual"
        elif "instalacion" in filename.lower():
            metadata["categoria"] = "instalacion"
        
        return metadata
    
    def search(
        self, 
        query: str, 
        filters: Optional[Dict[str, str]] = None,
        top_k: int = 5
    ) -> List[RAGDocument]:
        """
        Busca información relevante en la base de conocimiento.
        
        Args:
            query: Consulta de búsqueda
            filters: Filtros de metadata (marca, modelo, implemento)
            top_k: Cantidad de resultados a retornar
            
        Returns:
            Lista de documentos relevantes
        """
        # Implementación mejorada con scoring
        query_lower = query.lower()
        query_words = query_lower.split()
        scored_results = []
        
        for doc in self.documents:
            # Aplicar filtros de metadata
            if filters:
                match = all(
                    doc.metadata.get(key, "").lower() == value.lower()
                    for key, value in filters.items()
                )
                if not match:
                    continue
            
            # Calcular score basado en palabras coincidentes
            score = 0
            matched_words = set()
            doc_content_lower = doc.content.lower()
            
            for word in query_words:
                if word in doc_content_lower:
                    score += 1
                    matched_words.add(word)
            
            # Bonus por coincidencias exactas de términos técnicos
            if 'cvm' in matched_words and any(w in doc_content_lower for w in ['120', 'l']):
                score += 5  # Bonus para documentos que mencionan CVM y el modelo específico
            
            if score > 0:
                scored_results.append((score, doc))
        
        # Ordenar por score descendente
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        return [doc for score, doc in scored_results[:top_k]]
    
    def validate_compatibility(
        self,
        implemento: str,
        marca: str,
        modelo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Valida la compatibilidad de un implemento con una máquina.
        
        Args:
            implemento: Tipo de implemento (balde, martillo, etc)
            marca: Marca de la mini cargadora
            modelo: Modelo específico (opcional)
            
        Returns:
            Dict con resultado de validación y recomendaciones
        """
        query = f"compatibilidad {implemento} {marca} {modelo or ''}"
        filters = {"marca": marca}
        
        if modelo:
            filters["modelo"] = modelo
        
        results = self.search(query, filters=filters)
        
        if not results:
            return {
                "compatible": None,
                "confidence": 0.0,
                "message": "No hay información técnica disponible para validar compatibilidad",
                "requires_human": True
            }
        
        # Analizar resultados
        compatible = True
        confidence = 0.8
        recommendations = []
        
        for doc in results:
            content_lower = doc.content.lower()
            
            # Detectar palabras clave positivas
            if any(kw in content_lower for kw in ["compatible", "recomendado", "óptimo"]):
                recommendations.append(doc.content)
            
            # Detectar restricciones
            if any(kw in content_lower for kw in ["no compatible", "limitado", "restricción"]):
                compatible = False
                confidence = 0.3
        
        return {
            "compatible": compatible,
            "confidence": confidence,
            "message": f"Validación para {implemento} en {marca} {modelo or ''}",
            "recommendations": recommendations[:3],
            "requires_human": confidence < 0.5
        }
    
    def get_specifications(
        self,
        marca: str,
        modelo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene especificaciones técnicas de una máquina.
        
        Args:
            marca: Marca de la mini cargadora
            modelo: Modelo específico
            
        Returns:
            Dict con especificaciones técnicas
        """
        filters = {"marca": marca, "categoria": "especificaciones"}
        if modelo:
            filters["modelo"] = modelo
        
        results = self.search(f"{marca} {modelo or ''} especificaciones", filters=filters)
        
        if not results:
            return {
                "found": False,
                "message": "No hay especificaciones disponibles"
            }
        
        # Extraer datos del primer resultado
        doc = results[0]
        return {
            "found": True,
            "marca": marca,
            "modelo": modelo,
            "specifications": doc.content,
            "metadata": doc.metadata
        }
    
    def add_document(self, document: RAGDocument):
        """Agrega un documento a la base de conocimiento"""
        self.documents.append(document)
    
    def update_from_vector_db(self):
        """Actualiza la base de conocimiento desde la BD vectorial"""
        # TODO: Implementar sincronización con Pinecone/Weaviate
        pass


# Singleton para uso global
_rag_instance: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """Retorna la instancia singleton del sistema RAG"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
    return _rag_instance
