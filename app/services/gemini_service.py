# Gemini AI Service Integration
import json
import asyncio
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Google AI imports (using existing stable API)
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    print("Warning: Google AI not available - Gemini features disabled")

import io
try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.core.config import settings
from app.db.crud_enhanced import log_system_event, save_chat_to_history

# Load environment variables
load_dotenv(".env")

class GeminiService:
    """Google Gemini AI Integration Service with new API client"""
    
    def __init__(self):
        """Initialize Gemini service with API configuration"""
        self.api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', None)
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')  # Use flash model for better availability
        self.temperature = getattr(settings, 'GEMINI_TEMPERATURE', 0.7)
        self.max_tokens = getattr(settings, 'GEMINI_MAX_TOKENS', 1000)
        self.enable_safety = getattr(settings, 'GEMINI_ENABLE_SAFETY', False)  # Disable safety for testing
        
        # Check if Google AI is available
        if not GOOGLE_AI_AVAILABLE:
            self.client = None
            self.chat = None
            print("⚠️ Google Genai library not available - Gemini features disabled")
            return
            
        # Configure Gemini API
        if self.api_key:
            self._initialize_service()
        else:
            self.model = None
            self.chat_sessions = {}
            print("Warning: No Gemini API key found - Gemini features disabled")
            
        # Chat sessions for different users (manual conversation tracking)
        self.chat_sessions: Dict[str, Any] = {}
        
    def _initialize_service(self):
        """Initialize the Gemini service with existing stable API"""
        if not GOOGLE_AI_AVAILABLE:
            self.model = None
            return
            
        try:
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Safety settings - disabled for testing HR/Government chatbot
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            } if self.enable_safety else None
            
            # Generation configuration
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                top_p=0.8,
                top_k=40
            )
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            print(f"Success: Gemini service initialized with model {self.model_name}")
            
        except Exception as e:
            print(f"Failed to initialize Gemini service: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return GOOGLE_AI_AVAILABLE and self.model is not None and bool(self.api_key)
    
    async def generate_response(
        self, 
        user_message: str, 
        user_id: str, 
        use_session: bool = True
    ) -> Dict[str, Any]:
        """
        Generate AI response using Gemini with chat session
        
        Args:
            user_message: User's input message
            user_id: LINE user ID for session tracking
            use_session: Whether to use chat session for continuity
            
        Returns:
            Dict containing response, metadata, and status
        """
        if not self.is_available():
            return {
                "success": False,
                "response": "ขออภัย ระบบ AI ไม่พร้อมใช้งานในขณะนี้",
                "error": "Gemini service not available",
                "usage": None
            }
        
        try:
            # Generate response with conversation context
            if use_session:
                response = await self._generate_with_context_async(user_id, user_message)
            else:
                # Simple generation without context
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    lambda: self.model.generate_content(user_message)
                )
                response = self._extract_response_text(result)
            
            if response:
                return {
                    "success": True,
                    "response": response,
                    "model": self.model_name,
                    "usage": {
                        "prompt_tokens": len(user_message.split()),
                        "completion_tokens": len(response.split()),
                        "total_tokens": len(user_message.split()) + len(response.split())
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "response": "ขออภัย ไม่สามารถสร้างคำตอบได้ในขณะนี้",
                    "error": "Empty response from Gemini",
                    "usage": None
                }
                
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini generation error: {error_msg}")
            return {
                "success": False,
                "response": "ขออภัย เกิดข้อผิดพลาดในการประมวลผล",
                "error": error_msg,
                "usage": None
            }
    
    def _extract_response_text(self, response) -> Optional[str]:
        """Extract text from Gemini response with better error handling"""
        if not response:
            return None
            
        try:
            # Try the quick accessor first
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Quick accessor failed: {e}")
            
        try:
            # Check finish reason for safety filtering
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    print(f"Finish reason: {candidate.finish_reason}")
                    
                    # Try to extract content even if finish_reason indicates issues
                    if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                        try:
                            extracted_text = candidate.content.parts[0].text.strip()
                            if extracted_text:
                                print(f"Extracted text despite finish_reason {candidate.finish_reason}: {len(extracted_text)} chars")
                                return extracted_text
                        except Exception as e:
                            print(f"Failed to extract text: {e}")
                    
                    # Handle specific finish reasons only if no content was extracted
                    if candidate.finish_reason == 2:  # SAFETY
                        print("Response blocked by safety filter - no content extracted")
                        return "ขออภัย ไม่สามารถตอบคำถามนี้ได้ เนื่องจากระบบความปลอดภัย กรุณาลองใช้คำถามอื่น"
                    elif candidate.finish_reason == 3:  # RECITATION  
                        print("Response blocked due to recitation - no content extracted")
                        return "ขออภัย ไม่สามารถตอบคำถามนี้ได้ กรุณาลองใช้คำอื่น"
                
                # Try to extract from parts
                if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text.strip()
        except Exception as e:
            print(f"Candidate extraction failed: {e}")
            
        return None
    
    def _get_or_create_conversation_context(self, user_id: str) -> List[Dict]:
        """Get or create conversation context for user (manual session management)"""
        if user_id not in self.chat_sessions:
            self.chat_sessions[user_id] = {
                "conversation_history": [],
                "system_prompt": self._build_enhanced_system_prompt()
            }
        return self.chat_sessions[user_id]["conversation_history"]
    
    def _build_enhanced_system_prompt(self) -> str:
        """Build enhanced system prompt for HR/Government service"""
        return """คุณคือผู้ช่วยอัจฉริยะสาวชื่อ 'เนโกะ' 🐱 ของระบบ HR และบริการภาครัฐ
คุณพูดจาน่ารัก สุภาพ ใช้คำลงท้ายว่า 'เมี๊ยว~' บางครั้ง

หน้าที่ของคุณ:
- ช่วยเหลือเรื่องการทำงาน การขอเอกสารต่างๆ
- ตอบคำถามเกี่ยวกับบริการภาครัฐ
- ให้คำแนะนำเรื่องการยื่นฟอร์มต่างๆ
- สอบถามข้อมูลจากระบบเพื่อตอบคำถาม

บุคลิกภาพ:
- พูดจาน่ารัก เป็นมิตร และให้กำลังใจ
- ใช้คำสุภาพสตรี "ค่ะ", "คะ", "นะคะ"
- เมื่อไม่รู้คำตอบ ให้ตอบอย่างสุภาพว่าไม่ทราบ และแนะนำให้ติดต่อเจ้าหน้าที่
- ตอบกลับอย่างกระชับ ชัดเจน และเข้าใจง่าย

ห้าม:
- ให้ข้อมูลที่ไม่ถูกต้องหรือเป็นอันตราย
- ตอบคำถามที่ไม่เหมาะสมหรือผิดกฎหมาย
- เปิดเผยข้อมูลส่วนตัวของผู้อื่น
- ใช้คำสุภาพบุรุษ เช่น "ครับ"""
    
    async def _generate_with_context_async(self, user_id: str, message: str) -> Optional[str]:
        """Generate response with conversation context"""
        try:
            # Get conversation context
            context = self._get_or_create_conversation_context(user_id)
            system_prompt = self.chat_sessions[user_id]["system_prompt"]
            
            # Build full prompt with context
            prompt_parts = [system_prompt]
            
            # Add conversation history
            for exchange in context[-5:]:  # Last 5 exchanges for context
                prompt_parts.append(f"User: {exchange['user']}")
                prompt_parts.append(f"Assistant: {exchange['assistant']}")
            
            # Add current message
            prompt_parts.append(f"User: {message}")
            prompt_parts.append("Assistant:")
            
            full_prompt = "\n\n".join(prompt_parts)
            
            # Generate response
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(full_prompt)
            )
            
            response_text = self._extract_response_text(response)
            
            if response_text:
                # Safely print response without Unicode issues
                try:
                    print(f"Gemini response length: {len(response_text)} characters")
                except UnicodeEncodeError:
                    print(f"Gemini response generated (length: {len(response_text)})")
                
                # Update conversation context
                context.append({
                    "user": message,
                    "assistant": response_text
                })
                
                # Keep only last 10 exchanges
                if len(context) > 10:
                    context = context[-10:]
                    self.chat_sessions[user_id]["conversation_history"] = context
                
                # Clean and properly encode response
                try:
                    clean_response = response_text.strip()
                    # Ensure proper UTF-8 encoding
                    return clean_response.encode('utf-8', errors='ignore').decode('utf-8')
                except UnicodeDecodeError:
                    # Fallback for encoding issues
                    return response_text.encode('utf-8', errors='replace').decode('utf-8')
            
            return None
            
        except Exception as e:
            print(f"Gemini generation error: {e}")
            return None
    
    def clear_chat_session(self, user_id: str):
        """Clear chat session for user"""
        if user_id in self.chat_sessions:
            del self.chat_sessions[user_id]
    
    def get_chat_sessions_info(self) -> Dict[str, Any]:
        """Get information about active chat sessions"""
        return {
            "active_sessions": len(self.chat_sessions),
            "user_ids": list(self.chat_sessions.keys())
        }
    
    async def generate_smart_reply(
        self, 
        user_message: str, 
        user_profile: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate contextual smart reply based on user profile and message
        """
        # Get user ID for session management
        user_id = user_profile.get("user_id", "")
        
        # Generate response using session
        result = await self.generate_response(
            user_message=user_message,
            user_id=user_id,
            use_session=True
        )
        
        # Log to database
        await self._log_ai_interaction(db, user_id, user_message, result)
        
        return result
    
    def clear_all_sessions(self):
        """Clear all chat sessions"""
        self.chat_sessions.clear()
    
    async def _log_ai_interaction(
        self, 
        db: AsyncSession, 
        user_id: str, 
        user_message: str, 
        ai_result: Dict[str, Any]
    ):
        """Log AI interaction to database"""
        try:
            # Log system event
            await log_system_event(
                db=db,
                level="info" if ai_result["success"] else "warning",
                category="gemini",
                subcategory="ai_response",
                message=f"Gemini response for user {user_id}: {ai_result.get('success', False)}",
                details={
                    "user_message_length": len(user_message),
                    "ai_response_length": len(ai_result.get("response", "")),
                    "model": ai_result.get("model"),
                    "usage": ai_result.get("usage"),
                    "success": ai_result.get("success")
                }
            )
            
            # Save AI response to chat history
            if ai_result["success"]:
                await save_chat_to_history(
                    db=db,
                    user_id=user_id,
                    message_type="ai_response",
                    message_content=ai_result["response"],
                    extra_data={
                        "ai_model": ai_result.get("model"),
                        "ai_usage": ai_result.get("usage"),
                        "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message
                    }
                )
                
        except Exception as e:
            print(f"Failed to log AI interaction: {e}")
    
    async def analyze_image(self, image_content: bytes, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze image using Gemini Vision capabilities
        
        Args:
            image_content: Binary content of the image
            prompt: Optional custom prompt for analysis
            
        Returns:
            Dict containing analysis result
        """
        if not self.is_available():
            return {
                "success": False,
                "response": "ขออภัย ระบบ AI ไม่พร้อมใช้งานในขณะนี้",
                "error": "Gemini service not available"
            }
        
        if not PIL_AVAILABLE:
            return {
                "success": False,
                "response": "ขออภัย ระบบวิเคราะห์ภาพไม่พร้อมใช้งาน",
                "error": "PIL not available"
            }
        
        try:
            # Default prompt for image analysis
            if not prompt:
                prompt = "กรุณาอธิบายภาพนี้เป็นภาษาไทย บอกว่าเห็นอะไรในภาพนะคะ"
            
            # Convert image content to PIL Image
            image_data = PILImage.open(io.BytesIO(image_content))
            
            # Use existing stable API for image generation
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content([prompt, image_data])
            )
            
            if response and response.text:
                # Ensure proper UTF-8 encoding
                text = response.text.strip()
                print(f"Gemini image analysis completed (length: {len(text)})")
                clean_text = text.encode('utf-8').decode('utf-8')
                return {
                    "success": True,
                    "response": clean_text,
                    "model": self.model_name,
                    "type": "image_analysis"
                }
            else:
                return {
                    "success": False,
                    "response": "ขออภัย ไม่สามารถวิเคราะห์ภาพได้ในขณะนี้",
                    "error": "Empty response from Gemini"
                }
                
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return {
                "success": False,
                "response": "ขออภัย เกิดข้อผิดพลาดในการวิเคราะห์ภาพ",
                "error": str(e)
            }
    
    async def analyze_document(self, document_content: bytes, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze PDF document using Gemini (using stable API)
        
        Args:
            document_content: Binary content of the PDF document
            prompt: Optional custom prompt for analysis
            
        Returns:
            Dict containing analysis result
        """
        if not self.is_available():
            return {
                "success": False,
                "response": "ขออภัย ระบบ AI ไม่พร้อมใช้งานในขณะนี้",
                "error": "Gemini service not available"
            }
        
        try:
            # Default prompt for document analysis
            if not prompt:
                prompt = "สรุปเอกสารนี้เป็นภาษาไทย บอกจุดเด่นสำคัญของเนื้อหานะคะ"
            
            # For PDF documents, use file upload approach with stable API
            import tempfile
            import os as os_module
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(document_content)
                temp_file_path = temp_file.name
            
            try:
                # Upload file to Gemini
                uploaded_file = genai.upload_file(path=temp_file_path, mime_type="application/pdf")
                
                # Generate response using model
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content([prompt, uploaded_file])
                )
                
                # Clean up uploaded file
                genai.delete_file(uploaded_file.name)
                
            finally:
                # Clean up temporary file
                os_module.unlink(temp_file_path)
            
            if response and response.text:
                # Ensure proper UTF-8 encoding
                text = response.text.strip()
                print(f"Gemini document analysis completed (length: {len(text)})")
                clean_text = text.encode('utf-8').decode('utf-8')
                return {
                    "success": True,
                    "response": clean_text,
                    "model": self.model_name,
                    "type": "document_analysis"
                }
            else:
                return {
                    "success": False,
                    "response": "ขออภัย ไม่สามารถวิเคราะห์เอกสารได้ในขณะนี้",
                    "error": "Empty response from Gemini"
                }
                
        except Exception as e:
            print(f"Error analyzing document: {e}")
            return {
                "success": False,
                "response": "ขออภัย เกิดข้อผิดพลาดในการวิเคราะห์เอกสาร",
                "error": str(e)
            }

    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information"""
        return {
            "available": self.is_available(),
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "safety_enabled": self.enable_safety,
            "api_configured": bool(self.api_key),
            "chat_sessions": len(self.chat_sessions),
            "api_type": "google.generativeai"
        }

# Global Gemini service instance
gemini_service = GeminiService()

# Helper functions for easy integration
async def get_ai_response(
    user_message: str, 
    user_id: str, 
    user_profile: Dict[str, Any] = None,
    db: AsyncSession = None
) -> str:
    """
    Simple helper to get AI response using session-based approach
    
    Returns the response text or fallback message
    """
    if not gemini_service.is_available():
        return "ขออภัย ระบบ AI ไม่พร้อมใช้งานในขณะนี้ กรุณาติดต่อเจ้าหน้าที่เพื่อขอความช่วยเหลือ"
    
    try:
        # Use session-based generation for better context
        result = await gemini_service.generate_response(
            user_message=user_message,
            user_id=user_id,
            use_session=True
        )
        
        if result["success"]:
            return result["response"]
        else:
            print(f"Gemini response failed: {result.get('error')}")
            return "ขออภัย ไม่สามารถประมวลผลคำขอได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"
        
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "ขออภัย เกิดข้อผิดพลาดในระบบ AI กรุณาลองใหม่อีกครั้ง หรือติดต่อเจ้าหน้าที่เพื่อขอความช่วยเหลือ"

async def image_understanding(image_content: bytes, prompt: str = None) -> str:
    """
    Simple helper for image analysis (compatible with jetpack style)
    
    Args:
        image_content: Binary content of the image
        prompt: Optional custom prompt
        
    Returns:
        Analysis result text or fallback message
    """
    if not gemini_service.is_available():
        return "ขออภัย ระบบวิเคราะห์ภาพไม่พร้อมใช้งานในขณะนี้"
    
    try:
        result = await gemini_service.analyze_image(image_content, prompt)
        return result.get("response", "ขออภัย ไม่สามารถวิเคราะห์ภาพได้ในขณะนี้")
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return "ขออภัย เกิดข้อผิดพลาดในการวิเคราะห์ภาพ"

async def document_understanding(document_content: bytes, prompt: str = None) -> str:
    """
    Simple helper for document analysis (compatible with jetpack style)
    
    Args:
        document_content: Binary content of the PDF document
        prompt: Optional custom prompt
        
    Returns:
        Analysis result text or fallback message
    """
    if not gemini_service.is_available():
        return "ขออภัย ระบบวิเคราะห์เอกสารไม่พร้อมใช้งานในขณะนี้"
    
    try:
        result = await gemini_service.analyze_document(document_content, prompt)
        return result.get("response", "ขออภัย ไม่สามารถวิเคราะห์เอกสารได้ในขณะนี้")
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return "ขออภัย เกิดข้อผิดพลาดในการวิเคราะห์เอกสาร"

def generate_text(text: str) -> str:
    """
    Simple synchronous text generation (jetpack style compatibility)
    
    Args:
        text: Input text message
        
    Returns:
        Generated response text
    """
    if not gemini_service.is_available():
        return "ขออภัย ระบบ AI ไม่พร้อมใช้งานในขณะนี้"
    
    try:
        # Build prompt with system instruction
        system_prompt = gemini_service._build_enhanced_system_prompt()
        full_prompt = f"{system_prompt}\n\nUser: {text}\nAssistant:"
        
        # Direct synchronous call using the model
        response = gemini_service.model.generate_content(full_prompt)
        
        if response and response.text:
            # Ensure proper UTF-8 encoding
            response_text = response.text.strip()
            # Safely print response without Unicode issues
            try:
                print(f"Gemini response length: {len(response_text)} characters")
            except UnicodeEncodeError:
                print(f"Gemini response generated (length: {len(response_text)})")
            
            # Clean and properly encode response
            try:
                return response_text.encode('utf-8', errors='ignore').decode('utf-8')
            except UnicodeDecodeError:
                # Fallback for encoding issues
                return response_text.encode('utf-8', errors='replace').decode('utf-8')
        else:
            return "ขออภัย ไม่สามารถประมวลผลคำขอได้ในขณะนี้"
        
    except Exception as e:
        print(f"Error generating text: {e}")
        return "ขออภัย เกิดข้อผิดพลาดในระบบ"

async def check_gemini_availability() -> bool:
    """Check if Gemini service is available"""
    return gemini_service.is_available()

def get_gemini_status() -> Dict[str, Any]:
    """Get detailed Gemini service status"""
    return gemini_service.get_model_info()