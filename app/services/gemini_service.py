# Gemini AI Service Integration
import json
import asyncio
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Optional Google AI imports for compatibility
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    print("⚠️ Google AI not available - Gemini features disabled")

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
    """Google Gemini AI Integration Service with fallback support"""
    
    def __init__(self):
        """Initialize Gemini service with API configuration"""
        self.api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', None)
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
        self.temperature = getattr(settings, 'GEMINI_TEMPERATURE', 0.7)
        self.max_tokens = getattr(settings, 'GEMINI_MAX_TOKENS', 1000)
        self.enable_safety = getattr(settings, 'GEMINI_ENABLE_SAFETY', True)
        
        # Check if Google AI is available
        if not GOOGLE_AI_AVAILABLE:
<<<<<<< HEAD
            self.model = None
            print("⚠️ Google AI library not available - Gemini features disabled")
=======
            self.client = None
            self.model = None
            self.chat = None
            print("⚠️ Google Genai library not available - Gemini features disabled")
>>>>>>> b0f64fe (fix: resolve static file mounting and Gemini service initialization issues)
            return
            
        # Configure Gemini API
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self._initialize_model()
        else:
            self.model = None
<<<<<<< HEAD
            print("⚠️ No Gemini API key found - Gemini features disabled")
=======
            self.client = None
            self.chat_sessions = {}
            print("Warning: No Gemini API key found - Gemini features disabled")
>>>>>>> b0f64fe (fix: resolve static file mounting and Gemini service initialization issues)
            
        # Conversation context storage
        self.conversation_contexts: Dict[str, List[Dict]] = {}
        
    def _initialize_model(self):
        """Initialize the Gemini model with configuration"""
        if not GOOGLE_AI_AVAILABLE:
            self.model = None
            self.client = None
            return
            
        try:
            # Safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            } if self.enable_safety else {}
            
            # Generation configuration
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                top_p=0.8,
                top_k=40
            )
            
            # System instruction for Thai government service bot
            system_instruction = """คุณเป็นผู้ช่วยอัจฉริยะของระบบ LINE Bot สำหรับองค์กรภาครัฐ

หลักการตอบกลับ:
1. ใช้ภาษาไทยในการตอบกลับ
2. ตอบแบบสุภาพและเป็นมิตร
3. ให้ข้อมูลที่ถูกต้องและเป็นประโยชน์
4. หากไม่ทราบคำตอบ ให้แนะนำให้ติดต่อเจ้าหน้าที่
5. ตอบกลับอย่างกระชับและชัดเจน
6. หากเป็นคำถามเกี่ยวกับบริการภาครัฐ ให้ข้อมูลที่เป็นประโยชน์

ห้าม:
- ให้ข้อมูลที่ไม่ถูกต้องหรือเป็นอันตราย
- ตอบคำถามที่ไม่เหมาะสมหรือผิดกฎหมาย
- เปิดเผยข้อมูลส่วนตัวของผู้อื่น"""
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings if self.enable_safety else None,
                system_instruction=system_instruction
            )
            
<<<<<<< HEAD
=======
            # Set client to model for backward compatibility
            self.client = self.model
            
            print(f"Success: Gemini service initialized with model {self.model_name}")
            
>>>>>>> b0f64fe (fix: resolve static file mounting and Gemini service initialization issues)
        except Exception as e:
            print(f"Failed to initialize Gemini model: {e}")
            self.model = None
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return GOOGLE_AI_AVAILABLE and self.model is not None and bool(self.api_key)
    
    async def generate_response(
        self, 
        user_message: str, 
        user_id: str, 
        conversation_context: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response using Gemini
        
        Args:
            user_message: User's input message
            user_id: LINE user ID for context tracking
            conversation_context: Previous conversation messages
            system_prompt: Optional system instruction
            
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
            # Build conversation history
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add conversation context
            if conversation_context:
                messages.extend(conversation_context)
            
            # Add current user message
            messages.append({
                "role": "user", 
                "content": user_message
            })
            
            # Prepare prompt for Gemini
            prompt = self._build_gemini_prompt(messages)
            
            # Generate response
            response = await self._generate_async(prompt)
            
            if response:
                # Store conversation context
                self._update_conversation_context(user_id, user_message, response)
                
                return {
                    "success": True,
                    "response": response,
                    "model": self.model_name,
                    "usage": {
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": len(response.split()),
                        "total_tokens": len(prompt.split()) + len(response.split())
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
            return {
                "success": False,
                "response": "ขออภัย เกิดข้อผิดพลาดในการประมวลผล",
                "error": error_msg,
                "usage": None
            }
    
    async def _generate_async(self, prompt: str) -> Optional[str]:
        """Generate response asynchronously"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            if response and response.text:
                return response.text.strip()
            return None
            
        except Exception as e:
            print(f"Gemini generation error: {e}")
            return None
    
    def _build_gemini_prompt(self, messages: List[Dict]) -> str:
        """Build formatted prompt for Gemini"""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    def _update_conversation_context(self, user_id: str, user_message: str, ai_response: str):
        """Update conversation context for user"""
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = []
        
        context = self.conversation_contexts[user_id]
        
        # Add user message and AI response
        context.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Keep only last 10 exchanges (20 messages)
        if len(context) > 20:
            context = context[-20:]
        
        self.conversation_contexts[user_id] = context
    
    def get_conversation_context(self, user_id: str) -> List[Dict]:
        """Get conversation context for user"""
        return self.conversation_contexts.get(user_id, [])
    
    def clear_conversation_context(self, user_id: str):
        """Clear conversation context for user"""
        if user_id in self.conversation_contexts:
            del self.conversation_contexts[user_id]
    
    async def generate_smart_reply(
        self, 
        user_message: str, 
        user_profile: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate contextual smart reply based on user profile and message
        """
        # Build system prompt based on user profile
        system_prompt = self._build_system_prompt(user_profile)
        
        # Get conversation context
        user_id = user_profile.get("user_id", "")
        context = self.get_conversation_context(user_id)
        
        # Generate response
        result = await self.generate_response(
            user_message=user_message,
            user_id=user_id,
            conversation_context=context,
            system_prompt=system_prompt
        )
        
        # Log to database
        await self._log_ai_interaction(db, user_id, user_message, result)
        
        return result
    
    def _build_system_prompt(self, user_profile: Dict[str, Any]) -> str:
        """Build system prompt based on user profile"""
        user_name = user_profile.get("display_name", "ผู้ใช้")
        
        system_prompt = f"""คุณเป็นผู้ช่วยอัจฉริยะของระบบ LINE Bot สำหรับองค์กรภาครัฐ

ข้อมูลผู้ใช้:
- ชื่อ: {user_name}
- เวลาปัจจุบัน: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

หลักการตอบกลับ:
1. ใช้ภาษาไทยในการตอบกลับ
2. ตอบแบบสุภาพและเป็นมิตร
3. ให้ข้อมูลที่ถูกต้องและเป็นประโยชน์
4. หากไม่ทราบคำตอบ ให้แนะนำให้ติดต่อเจ้าหน้าที่
5. ตอบกลับอย่างกระชับและชัดเจน
6. หากเป็นคำถามเกี่ยวกับบริการภาครัฐ ให้ข้อมูลที่เป็นประโยชน์

ห้าม:
- ให้ข้อมูลที่ไม่ถูกต้องหรือเป็นอันตราย
- ตอบคำถามที่ไม่เหมาะสมหรือผิดกฎหมาย
- เปิดเผยข้อมูลส่วนตัวของผู้อื่น"""

        return system_prompt
    
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
                    metadata={
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
        
        try:
            # Default prompt for image analysis
            if not prompt:
                prompt = "กรุณาอธิบายรายละเอียดของภาพนี้เป็นภาษาไทย โดยครอบคลุมสิ่งที่เห็นในภาพ"
            
            # Convert image content to PIL Image
            image = PILImage.open(io.BytesIO(image_content))
            
            # Generate response using model
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content([prompt, image])
            )
            
            if response and response.text:
                return {
                    "success": True,
                    "response": response.text.strip(),
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
            return {
                "success": False,
                "response": "ขออภัย เกิดข้อผิดพลาดในการวิเคราะห์ภาพ",
                "error": str(e)
            }
    
    async def analyze_document(self, document_content: bytes, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze PDF document using Gemini
        
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
                prompt = "กรุณาสรุปเนื้อหาสำคัญของเอกสารนี้เป็นภาษาไทย"
            
            # For PDF documents, we need to use file upload approach
            # Save temporary file and upload
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
                return {
                    "success": True,
                    "response": response.text.strip(),
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
            "api_configured": bool(self.api_key)
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
    Simple helper to get AI response
    
    Returns the response text or fallback message
    """
    if not gemini_service.is_available():
        return "ขออภัย ระบบ AI ไม่พร้อมใช้งานในขณะนี้ กรุณาติดต่อเจ้าหน้าที่เพื่อขอความช่วยเหลือ"
    
    try:
        # Use the synchronous generate_text function to avoid async deadlocks
        response = generate_text(user_message)
        
        # Log the interaction if database is available
        if db and user_profile:
            try:
                await gemini_service._log_ai_interaction(
                    db=db, 
                    user_id=user_id, 
                    user_message=user_message,
                    ai_result={"success": True, "response": response, "model": gemini_service.model_name}
                )
            except Exception as log_e:
                print(f"Failed to log AI interaction: {log_e}")
        
        return response
        
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "ขออภัย เกิดข้อผิดพลาดในระบบ กรุณาลองใหม่อีกครั้ง"

async def image_understanding(image_content: bytes, prompt: str = None) -> str:
    """
    Simple helper for image analysis
    
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
    Simple helper for document analysis
    
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
    Simple synchronous text generation (for compatibility)
    
    Args:
        text: Input text message
        
    Returns:
        Generated response text
    """
    if not gemini_service.is_available():
        return "ขออภัย ระบบ AI ไม่พร้อมใช้งานในขณะนี้"
    
    try:
        # Direct synchronous call using the model
        response = gemini_service.model.generate_content(text)
        
        if response and response.text:
            return response.text.strip()
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