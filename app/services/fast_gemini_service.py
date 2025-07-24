# Fast Gemini Service - Optimized for Quick Responses
import asyncio
import time
from typing import Dict, Optional, Any
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

# Optional Google AI imports for compatibility
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold, GenerateContentResponse
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    print("Warning: Google AI not available - Gemini features disabled")

from app.core.config import settings

class FastGeminiService:
    """Optimized Gemini AI Service for fast responses"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.model_name = 'gemini-1.5-flash'  # Fastest model
        self.model = None
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.timeout = 10  # 10 second timeout
        self.max_retries = 2
        
        # Performance tracking
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
        
        if GOOGLE_AI_AVAILABLE and self.api_key:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model with optimized settings"""
        try:
            genai.configure(api_key=self.api_key)
            
            # Optimized generation config for speed
            generation_config = {
                "temperature": 0.5,  # Lower temperature for faster, more focused responses
                "top_p": 0.8,       # Reduced top_p for faster generation
                "top_k": 20,        # Lower top_k for speed
                "max_output_tokens": 500,  # Shorter responses for speed
            }
            
            # Minimal safety settings for speed (adjust as needed)
            safety_settings = [
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE}
            ]
            
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            print(f"✅ Fast Gemini model initialized: {self.model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini model: {e}")
            self.model = None
            return False
    
    async def _wait_for_rate_limit(self):
        """Implement simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    @asynccontextmanager
    async def _timeout_context(self, timeout_seconds: int):
        """Context manager for request timeout"""
        try:
            yield await asyncio.wait_for(
                self._make_request_context(),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            print(f"⏰ Gemini request timed out after {timeout_seconds} seconds")
            raise
    
    async def get_fast_response(
        self, 
        message: str, 
        context: Optional[str] = None,
        max_length: int = 300
    ) -> str:
        """
        Get fast response from Gemini AI with optimization
        
        Args:
            message: User message
            context: Optional context for the conversation
            max_length: Maximum response length (characters)
        
        Returns:
            str: AI response or fallback message
        """
        start_time = time.time()
        
        try:
            if not self.model:
                return self._get_fallback_response(message)
            
            # Optimize prompt for speed
            optimized_prompt = self._optimize_prompt(message, context, max_length)
            
            # Apply rate limiting
            await self._wait_for_rate_limit()
            
            # Make request with timeout
            response = await self._make_request_with_retry(optimized_prompt)
            
            # Track performance
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.success_count += 1
            
            # Keep only last 100 response times for averaging
            if len(self.response_times) > 100:
                self.response_times = self.response_times[-100:]
            
            print(f"✅ Fast Gemini response in {response_time:.2f}s")
            
            # Clean and truncate response
            cleaned_response = self._clean_response(response, max_length)
            return cleaned_response
            
        except Exception as e:
            self.error_count += 1
            response_time = time.time() - start_time
            print(f"❌ Gemini error after {response_time:.2f}s: {e}")
            
            return self._get_fallback_response(message)
    
    def _optimize_prompt(self, message: str, context: Optional[str], max_length: int) -> str:
        """Optimize prompt for faster processing"""
        
        # Base prompt optimized for Thai responses
        base_prompt = "ตอบคำถามนี้อย่างกระชับและเป็นประโยชน์เป็นภาษาไทย:\n\n"
        
        # Add context if provided (keep it short)
        if context:
            base_prompt += f"บริบท: {context[:100]}...\n\n"
        
        # Add message
        base_prompt += f"คำถาม: {message}\n\n"
        
        # Add length constraint
        if max_length < 500:
            base_prompt += f"ตอบในขอบเขต {max_length} ตัวอักษร "
        
        base_prompt += "โดยให้ข้อมูลที่ถูกต้องและชัดเจน"
        
        return base_prompt
    
    async def _make_request_with_retry(self, prompt: str) -> str:
        """Make request with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    # Exponential backoff
                    delay = 0.5 * (2 ** attempt)
                    print(f"🔄 Retrying Gemini request (attempt {attempt + 1}) after {delay}s delay")
                    await asyncio.sleep(delay)
                
                # Make the actual request
                response = await asyncio.wait_for(
                    self._make_gemini_request(prompt),
                    timeout=self.timeout
                )
                
                return response
                
            except Exception as e:
                last_error = e
                print(f"⚠️ Gemini request attempt {attempt + 1} failed: {e}")
                
                # Don't retry on certain errors
                if "API key" in str(e) or "quota" in str(e).lower():
                    break
        
        raise last_error or Exception("All retry attempts failed")
    
    async def _make_gemini_request(self, prompt: str) -> str:
        """Make the actual Gemini API request"""
        loop = asyncio.get_event_loop()
        
        # Run the synchronous Gemini API call in a thread pool
        response = await loop.run_in_executor(
            None, 
            self.model.generate_content, 
            prompt
        )
        
        if response and response.text:
            return response.text
        else:
            raise Exception("Empty response from Gemini API")
    
    def _clean_response(self, response: str, max_length: int) -> str:
        """Clean and optimize the response"""
        if not response:
            return "ขออภัย ไม่สามารถประมวลผลได้ในขณะนี้"
        
        # Remove excessive whitespace
        cleaned = ' '.join(response.strip().split())
        
        # Truncate if too long
        if len(cleaned) > max_length:
            # Try to truncate at sentence boundary
            sentences = cleaned.split('.')
            truncated = ""
            
            for sentence in sentences:
                if len(truncated + sentence + '.') <= max_length - 10:
                    truncated += sentence + '.'
                else:
                    break
            
            if truncated:
                cleaned = truncated
            else:
                cleaned = cleaned[:max_length-3] + "..."
        
        return cleaned
    
    def _get_fallback_response(self, message: str) -> str:
        """Get fallback response when Gemini is unavailable"""
        
        # Simple keyword-based responses for common queries
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['สวัสดี', 'หวัดดี', 'hello', 'hi']):
            return "สวัสดีครับ! ยินดีที่ได้รับใช้คุณ มีอะไรให้ช่วยเหลือไหมครับ?"
        
        elif any(word in message_lower for word in ['ขอบคุณ', 'thank']):
            return "ยินดีครับ! หากมีคำถามเพิ่มเติม สามารถสอบถามได้เสมอนะครับ"
        
        elif any(word in message_lower for word in ['ลาก่อน', 'bye']):
            return "ลาก่อนครับ! ขอบคุณที่ใช้บริการ หวังว่าจะได้พบกันใหม่ครับ"
        
        elif '?' in message or 'อะไร' in message_lower or 'ไง' in message_lower:
            return "ขออภัยครับ ระบบ AI กำลังประมวลผลไม่ได้ในขณะนี้ กรุณาลองใหม่อีกครั้งหรือติดต่อเจ้าหน้าที่เพื่อความช่วยเหลือครับ"
        
        else:
            return "ขอบคุณสำหรับข้อความครับ ขณะนี้ระบบ AI กำลังไม่พร้อมใช้งาน กรุณาลองใหม่อีกครั้งในอีกสักครู่ หรือติดต่อเจ้าหน้าที่ได้เลยครับ"
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "average_response_time": round(avg_response_time, 2),
            "success_count": self.success_count,
            "error_count": self.error_count,
            "total_requests": self.success_count + self.error_count,
            "success_rate": round(self.success_count / max(1, self.success_count + self.error_count) * 100, 1),
            "last_10_response_times": self.response_times[-10:] if self.response_times else []
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            if not self.model:
                return {"status": "unhealthy", "reason": "Model not initialized"}
            
            # Quick test
            test_response = await self.get_fast_response(
                "ทดสอบระบบ", 
                max_length=50
            )
            
            if test_response and not test_response.startswith("ขออภัย"):
                return {
                    "status": "healthy", 
                    "model": self.model_name,
                    "performance": self.get_performance_stats()
                }
            else:
                return {"status": "degraded", "reason": "Getting fallback responses"}
                
        except Exception as e:
            return {"status": "unhealthy", "reason": str(e)}

# Global service instance
fast_gemini_service = FastGeminiService()

# Convenience functions
async def get_ai_response_fast(message: str, context: Optional[str] = None) -> str:
    """Get fast AI response - main function to use"""
    return await fast_gemini_service.get_fast_response(message, context)

async def check_gemini_availability() -> bool:
    """Check if Gemini AI is available and working"""
    health = await fast_gemini_service.health_check()
    return health["status"] in ["healthy", "degraded"]

def get_gemini_status() -> Dict[str, Any]:
    """Get comprehensive status of Gemini service"""
    return {
        "available": GOOGLE_AI_AVAILABLE and fast_gemini_service.model is not None,
        "model": fast_gemini_service.model_name,
        "performance": fast_gemini_service.get_performance_stats()
    }

print("✅ Fast Gemini Service initialized")
