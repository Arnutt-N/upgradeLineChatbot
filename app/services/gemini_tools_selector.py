# Gemini AI Tools Selector for LINE Bot Message Processing
"""
Intelligent tool selection system that determines the most appropriate Gemini AI function
to call based on the LINE message type and content analysis.

This module acts as a smart router that:
1. Analyzes incoming message type and content
2. Selects optimal Gemini AI tool/function
3. Provides context-aware prompts
4. Handles tool-specific error cases
5. Returns structured responses
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.gemini_service import (
    get_ai_response, image_understanding, document_understanding,
    check_gemini_availability, gemini_service
)
from app.db.crud_enhanced import log_system_event

class MessageType(Enum):
    """Enumeration of supported message types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"
    STICKER = "sticker"
    POSTBACK = "postback"
    QUICK_REPLY = "quick_reply"
    IMAGEMAP = "imagemap"
    TEMPLATE = "template"
    FLEX = "flex"
    CAROUSEL_FLEX = "carousel_flex"
    UNKNOWN = "unknown"

class GeminiTool(Enum):
    """Enumeration of available Gemini AI tools"""
    TEXT_GENERATION = "text_generation"
    IMAGE_ANALYSIS = "image_analysis"
    DOCUMENT_ANALYSIS = "document_analysis"
    CONVERSATION = "conversation"
    LOCATION_CONTEXT = "location_context"
    EMOTION_ANALYSIS = "emotion_analysis"
    CONTENT_MODERATION = "content_moderation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"

@dataclass
class ToolSelection:
    """Data class for tool selection results"""
    tool: GeminiTool
    prompt: str
    context: Dict[str, Any]
    confidence: float
    fallback_tools: List[GeminiTool]
    metadata: Dict[str, Any]

@dataclass
class ProcessingResult:
    """Data class for processing results"""
    success: bool
    response: str
    tool_used: GeminiTool
    processing_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None

class GeminiToolsSelector:
    """Intelligent tool selector for Gemini AI integration"""
    
    def __init__(self):
        self.tool_mappings = self._initialize_tool_mappings()
        self.context_enhancers = self._initialize_context_enhancers()
        self.prompt_templates = self._initialize_prompt_templates()
        
    def _initialize_tool_mappings(self) -> Dict[MessageType, List[Tuple[GeminiTool, float]]]:
        """Initialize message type to tool mappings with confidence scores"""
        return {
            MessageType.TEXT: [
                (GeminiTool.CONVERSATION, 0.9),
                (GeminiTool.QUESTION_ANSWERING, 0.8),
                (GeminiTool.TEXT_GENERATION, 0.7),
                (GeminiTool.TRANSLATION, 0.5)
            ],
            MessageType.IMAGE: [
                (GeminiTool.IMAGE_ANALYSIS, 0.95),
                (GeminiTool.CONTENT_MODERATION, 0.3),
                (GeminiTool.TEXT_GENERATION, 0.2)
            ],
            MessageType.FILE: [
                (GeminiTool.DOCUMENT_ANALYSIS, 0.9),
                (GeminiTool.SUMMARIZATION, 0.8),
                (GeminiTool.QUESTION_ANSWERING, 0.6)
            ],
            MessageType.LOCATION: [
                (GeminiTool.LOCATION_CONTEXT, 0.9),
                (GeminiTool.TEXT_GENERATION, 0.7),
                (GeminiTool.QUESTION_ANSWERING, 0.5)
            ],
            MessageType.STICKER: [
                (GeminiTool.EMOTION_ANALYSIS, 0.8),
                (GeminiTool.TEXT_GENERATION, 0.6)
            ],
            MessageType.AUDIO: [
                (GeminiTool.TEXT_GENERATION, 0.7),
                (GeminiTool.CONVERSATION, 0.6)
            ],
            MessageType.VIDEO: [
                (GeminiTool.TEXT_GENERATION, 0.7),
                (GeminiTool.CONTENT_MODERATION, 0.4)
            ],
            MessageType.POSTBACK: [
                (GeminiTool.QUESTION_ANSWERING, 0.8),
                (GeminiTool.TEXT_GENERATION, 0.7)
            ]
        }
    
    def _initialize_context_enhancers(self) -> Dict[MessageType, callable]:
        """Initialize context enhancement functions for each message type"""
        return {
            MessageType.TEXT: self._enhance_text_context,
            MessageType.IMAGE: self._enhance_image_context,
            MessageType.FILE: self._enhance_file_context,
            MessageType.LOCATION: self._enhance_location_context,
            MessageType.STICKER: self._enhance_sticker_context,
            MessageType.AUDIO: self._enhance_audio_context,
            MessageType.VIDEO: self._enhance_video_context,
            MessageType.POSTBACK: self._enhance_postback_context
        }
    
    def _initialize_prompt_templates(self) -> Dict[GeminiTool, str]:
        """Initialize prompt templates for each Gemini tool"""
        return {
            GeminiTool.CONVERSATION: """
คุณเป็นผู้ช่วยอัจฉริยะของระบบ LINE Bot สำหรับองค์กรภาครัฐ

ข้อมูลผู้ใช้:
- ชื่อ: {user_name}
- เวลา: {current_time}

ข้อความจากผู้ใช้: "{user_message}"

กรุณาตอบกลับอย่างสุภาพเป็นภาษาไทย โดย:
1. ให้ข้อมูลที่ถูกต้องและเป็นประโยชน์
2. ตอบแบบกระชับและเข้าใจง่าย
3. หากไม่ทราบคำตอบ ให้แนะนำให้ติดต่อเจ้าหน้าที่
4. ใช้น้ำเสียงเป็นมิตรและเป็นทางการเล็กน้อย

{additional_context}
""",
            
            GeminiTool.IMAGE_ANALYSIS: """
กรุณาวิเคราะห์รูปภาพนี้อย่างละเอียดเป็นภาษาไทย สำหรับผู้ใช้ชื่อ {user_name}

โปรดอธิบาย:
1. สิ่งที่เห็นในภาพโดยทั่วไป
2. รายละเอียดที่สำคัญ (สี, วัตถุ, คน, สถานที่)
3. บริบทหรือเหตุการณ์ที่เกิดขึ้น
4. ข้อมูลที่เป็นประโยชน์หรือข้อสังเกต

หากเป็นเอกสาร ป้าย หรือข้อความในภาพ กรุณาอ่านและแปลความหมายด้วย

{additional_context}
""",
            
            GeminiTool.DOCUMENT_ANALYSIS: """
กรุณาวิเคราะห์และสรุปเอกสารนี้เป็นภาษาไทย สำหรับผู้ใช้ชื่อ {user_name}

โปรดให้ข้อมูล:
1. ประเด็นหลักของเอกสาร
2. ข้อมูลสำคัญที่ควรทราบ
3. สรุปเนื้อหาแบบกระชับ
4. ข้อเสนอแนะหรือขั้นตอนต่อไป (ถ้ามี)

หากเป็นแบบฟอร์มหรือเอกสารราชการ กรุณาอธิบายวัตถุประสงค์และวิธีการดำเนินการ

{additional_context}
""",
            
            GeminiTool.LOCATION_CONTEXT: """
ผู้ใช้ชื่อ {user_name} ได้แชร์ตำแหน่งที่ตั้ง:

ข้อมูลสถานที่:
- ชื่อ: {location_title}
- ที่อยู่: {location_address}
- พิกัด: {latitude}, {longitude}

กรุณาให้ข้อมูลเป็นภาษาไทยเกี่ยวกับ:
1. บริบทของสถานที่นี้
2. บริการหรือข้อมูลที่เกี่ยวข้อง
3. คำแนะนำที่เป็นประโยชน์
4. ข้อมูลเพิ่มเติมที่ผู้ใช้ควรทราบ

หากเป็นหน่วยงานราชการ โรงพยาบาล หรือสถานที่สำคัญ กรุณาให้ข้อมูลบริการ

{additional_context}
""",
            
            GeminiTool.EMOTION_ANALYSIS: """
ผู้ใช้ชื่อ {user_name} ได้ส่งสติกเกอร์:
- Package ID: {package_id}
- Sticker ID: {sticker_id}

กรุณาตอบกลับอย่างเหมาะสมเป็นภาษาไทย โดยพิจารณา:
1. อารมณ์หรือความรู้สึกที่สติกเกอร์แสดงออก
2. การตอบสนองที่เหมาะสม
3. การเสนอความช่วยเหลือหากจำเป็น

ใช้น้ำเสียงที่อบอุ่นและเข้าใจอารมณ์ของผู้ใช้

{additional_context}
""",
            
            GeminiTool.QUESTION_ANSWERING: """
ผู้ใช้ชื่อ {user_name} มีคำถาม: "{user_question}"

กรุณาตอบคำถามเป็นภาษาไทยอย่างครบถ้วน โดย:
1. ให้คำตอบที่ตรงประเด็น
2. อธิบายเพิ่มเติมหากจำเป็น
3. ให้ขั้นตอนการดำเนินการ (ถ้ามี)
4. แนะนำแหล่งข้อมูลเพิ่มเติม

หากไม่ทราบคำตอบที่แน่ชัด กรุณาแนะนำให้ติดต่อเจ้าหน้าที่ที่เกี่ยวข้อง

{additional_context}
"""
        }
    
    async def select_tool(self, message_type: MessageType, content: Dict[str, Any], 
                         user_profile: Dict[str, Any], db: AsyncSession) -> ToolSelection:
        """
        Select the most appropriate Gemini tool for processing
        
        Args:
            message_type: Type of the incoming message
            content: Message content and metadata
            user_profile: User profile information
            db: Database session for logging
            
        Returns:
            ToolSelection object with tool and configuration
        """
        try:
            # Get tool candidates
            tool_candidates = self.tool_mappings.get(message_type, [(GeminiTool.TEXT_GENERATION, 0.5)])
            
            # Analyze content for better tool selection
            content_analysis = await self._analyze_content(content, message_type)
            
            # Adjust confidence scores based on content analysis
            adjusted_candidates = self._adjust_tool_confidence(tool_candidates, content_analysis)
            
            # Select the highest confidence tool
            best_tool, confidence = max(adjusted_candidates, key=lambda x: x[1])
            
            # Generate enhanced prompt
            prompt = await self._generate_enhanced_prompt(
                best_tool, message_type, content, user_profile, content_analysis
            )
            
            # Prepare context
            context = await self._prepare_context(message_type, content, user_profile)
            
            # Get fallback tools
            fallback_tools = [tool for tool, _ in adjusted_candidates if tool != best_tool][:2]
            
            # Create selection result
            selection = ToolSelection(
                tool=best_tool,
                prompt=prompt,
                context=context,
                confidence=confidence,
                fallback_tools=fallback_tools,
                metadata={
                    "message_type": message_type.value,
                    "content_analysis": content_analysis,
                    "selection_time": datetime.now().isoformat()
                }
            )
            
            # Log tool selection
            await log_system_event(
                db=db,
                level="info",
                category="gemini_tools",
                subcategory="tool_selected",
                message=f"Selected {best_tool.value} for {message_type.value} with confidence {confidence:.2f}",
                user_id=user_profile.get('user_id', 'unknown'),
                details=selection.metadata
            )
            
            return selection
            
        except Exception as e:
            # Fallback selection
            await log_system_event(
                db=db, level="error", category="gemini_tools", subcategory="selection_error",
                message=f"Tool selection failed: {str(e)}", 
                user_id=user_profile.get('user_id', 'unknown')
            )
            
            return ToolSelection(
                tool=GeminiTool.TEXT_GENERATION,
                prompt=f"กรุณาตอบคำถามของผู้ใช้ชื่อ {user_profile.get('display_name', 'ผู้ใช้')} เป็นภาษาไทย",
                context={},
                confidence=0.5,
                fallback_tools=[],
                metadata={"error": str(e)}
            )
    
    async def process_with_tool(self, selection: ToolSelection, content: Dict[str, Any], 
                              user_profile: Dict[str, Any], db: AsyncSession) -> ProcessingResult:
        """
        Process content using the selected Gemini tool
        
        Args:
            selection: Tool selection result
            content: Message content
            user_profile: User profile
            db: Database session
            
        Returns:
            ProcessingResult with response and metadata
        """
        start_time = datetime.now()
        
        try:
            # Check Gemini availability
            if not await check_gemini_availability():
                return ProcessingResult(
                    success=False,
                    response="ขออภัย ระบบ AI ไม่พร้อมใช้งานในขณะนี้ กรุณาลองใหม่อีกครั้ง",
                    tool_used=selection.tool,
                    processing_time=0.0,
                    metadata={"error": "gemini_unavailable"},
                    error="Gemini service unavailable"
                )
            
            # Route to appropriate processing function
            if selection.tool == GeminiTool.IMAGE_ANALYSIS:
                response = await self._process_image_analysis(selection, content)
            elif selection.tool == GeminiTool.DOCUMENT_ANALYSIS:
                response = await self._process_document_analysis(selection, content)
            elif selection.tool in [GeminiTool.CONVERSATION, GeminiTool.TEXT_GENERATION, 
                                   GeminiTool.QUESTION_ANSWERING]:
                response = await self._process_text_generation(selection, user_profile, db)
            elif selection.tool == GeminiTool.LOCATION_CONTEXT:
                response = await self._process_location_context(selection, content, user_profile, db)
            elif selection.tool == GeminiTool.EMOTION_ANALYSIS:
                response = await self._process_emotion_analysis(selection, content, user_profile, db)
            else:
                response = await self._process_fallback(selection, user_profile, db)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Log successful processing
            await log_system_event(
                db=db, level="info", category="gemini_tools", subcategory="processing_success",
                message=f"Successfully processed with {selection.tool.value}",
                user_id=user_profile.get('user_id', 'unknown'),
                details={
                    "tool": selection.tool.value,
                    "processing_time": processing_time,
                    "response_length": len(response)
                }
            )
            
            return ProcessingResult(
                success=True,
                response=response,
                tool_used=selection.tool,
                processing_time=processing_time,
                metadata={
                    "confidence": selection.confidence,
                    "prompt_length": len(selection.prompt),
                    "context_keys": list(selection.context.keys())
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Log processing error
            await log_system_event(
                db=db, level="error", category="gemini_tools", subcategory="processing_error",
                message=f"Processing failed with {selection.tool.value}: {str(e)}",
                user_id=user_profile.get('user_id', 'unknown')
            )
            
            # Try fallback tools
            if selection.fallback_tools:
                try:
                    fallback_tool = selection.fallback_tools[0]
                    fallback_selection = ToolSelection(
                        tool=fallback_tool,
                        prompt=selection.prompt,
                        context=selection.context,
                        confidence=0.3,
                        fallback_tools=[],
                        metadata={"is_fallback": True}
                    )
                    return await self.process_with_tool(fallback_selection, content, user_profile, db)
                except:
                    pass
            
            # Final fallback
            return ProcessingResult(
                success=False,
                response="ขออภัย เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้ง หรือติดต่อเจ้าหน้าที่",
                tool_used=selection.tool,
                processing_time=processing_time,
                metadata={"error": str(e)},
                error=str(e)
            )
    
    # Content analysis methods
    
    async def _analyze_content(self, content: Dict[str, Any], message_type: MessageType) -> Dict[str, Any]:
        """Analyze content to improve tool selection"""
        analysis = {
            "complexity": "simple",
            "language": "thai",
            "intent": "general",
            "requires_specialized_tool": False
        }
        
        if message_type == MessageType.TEXT:
            text = content.get('text', '')
            
            # Complexity analysis
            if len(text) > 100:
                analysis["complexity"] = "complex"
            
            # Intent detection
            question_words = ['อะไร', 'ที่ไหน', 'เมื่อไหร่', 'ทำไม', 'อย่างไร', 'ใคร']
            if any(word in text for word in question_words):
                analysis["intent"] = "question"
            
            help_words = ['ช่วย', 'ติดต่อ', 'เจ้าหน้าที่', 'admin']
            if any(word in text.lower() for word in help_words):
                analysis["intent"] = "help_request"
        
        elif message_type == MessageType.IMAGE:
            analysis["requires_specialized_tool"] = True
            analysis["intent"] = "image_analysis"
        
        elif message_type == MessageType.FILE:
            file_name = content.get('file_name', '')
            if file_name.lower().endswith('.pdf'):
                analysis["requires_specialized_tool"] = True
                analysis["intent"] = "document_analysis"
        
        return analysis
    
    def _adjust_tool_confidence(self, candidates: List[Tuple[GeminiTool, float]], 
                               analysis: Dict[str, Any]) -> List[Tuple[GeminiTool, float]]:
        """Adjust tool confidence based on content analysis"""
        adjusted = []
        
        for tool, confidence in candidates:
            new_confidence = confidence
            
            # Boost specialized tools when needed
            if analysis.get("requires_specialized_tool", False):
                if tool in [GeminiTool.IMAGE_ANALYSIS, GeminiTool.DOCUMENT_ANALYSIS]:
                    new_confidence += 0.2
            
            # Boost question answering for questions
            if analysis.get("intent") == "question" and tool == GeminiTool.QUESTION_ANSWERING:
                new_confidence += 0.15
            
            # Boost conversation tool for help requests
            if analysis.get("intent") == "help_request" and tool == GeminiTool.CONVERSATION:
                new_confidence += 0.1
            
            adjusted.append((tool, min(new_confidence, 1.0)))
        
        return adjusted
    
    # Prompt generation methods
    
    async def _generate_enhanced_prompt(self, tool: GeminiTool, message_type: MessageType,
                                      content: Dict[str, Any], user_profile: Dict[str, Any],
                                      content_analysis: Dict[str, Any]) -> str:
        """Generate enhanced prompt for the selected tool"""
        template = self.prompt_templates.get(tool, self.prompt_templates[GeminiTool.CONVERSATION])
        
        # Base context
        context_vars = {
            "user_name": user_profile.get('display_name', 'ผู้ใช้'),
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "additional_context": ""
        }
        
        # Add content-specific variables
        if message_type == MessageType.TEXT:
            context_vars["user_message"] = content.get('text', '')
            context_vars["user_question"] = content.get('text', '')
        
        elif message_type == MessageType.LOCATION:
            context_vars.update({
                "location_title": content.get('title', 'ไม่ระบุ'),
                "location_address": content.get('address', 'ไม่ระบุ'),
                "latitude": content.get('latitude', 0),
                "longitude": content.get('longitude', 0)
            })
        
        elif message_type == MessageType.STICKER:
            context_vars.update({
                "package_id": content.get('package_id', ''),
                "sticker_id": content.get('sticker_id', '')
            })
        
        # Add context based on analysis
        if content_analysis.get("intent") == "help_request":
            context_vars["additional_context"] = "\nผู้ใช้ต้องการความช่วยเหลือเร่งด่วน กรุณาให้คำแนะนำที่ชัดเจนและเป็นประโยชน์"
        
        elif content_analysis.get("complexity") == "complex":
            context_vars["additional_context"] = "\nคำถามมีความซับซ้อน กรุณาตอบอย่างละเอียดและครบถ้วน"
        
        return template.format(**context_vars)
    
    # Context enhancement methods
    
    async def _prepare_context(self, message_type: MessageType, content: Dict[str, Any],
                             user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for processing"""
        enhancer = self.context_enhancers.get(message_type, lambda x, y, z: {})
        return enhancer(content, user_profile, {})
    
    def _enhance_text_context(self, content: Dict[str, Any], user_profile: Dict[str, Any], 
                            base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for text messages"""
        return {
            **base_context,
            "message_length": len(content.get('text', '')),
            "user_name": user_profile.get('display_name', 'ผู้ใช้'),
            "message_type": "text"
        }
    
    def _enhance_image_context(self, content: Dict[str, Any], user_profile: Dict[str, Any],
                             base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for image messages"""
        return {
            **base_context,
            "analysis_type": "image_vision",
            "user_name": user_profile.get('display_name', 'ผู้ใช้'),
            "message_id": content.get('message_id', '')
        }
    
    def _enhance_file_context(self, content: Dict[str, Any], user_profile: Dict[str, Any],
                            base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for file messages"""
        return {
            **base_context,
            "file_name": content.get('file_name', ''),
            "file_size": content.get('file_size', 0),
            "analysis_type": "document_analysis"
        }
    
    def _enhance_location_context(self, content: Dict[str, Any], user_profile: Dict[str, Any],
                                base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for location messages"""
        return {
            **base_context,
            "coordinates": (content.get('latitude', 0), content.get('longitude', 0)),
            "location_data": content
        }
    
    def _enhance_sticker_context(self, content: Dict[str, Any], user_profile: Dict[str, Any],
                               base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for sticker messages"""
        return {
            **base_context,
            "sticker_data": content,
            "emotion_analysis": True
        }
    
    def _enhance_audio_context(self, content: Dict[str, Any], user_profile: Dict[str, Any],
                             base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for audio messages"""
        return {
            **base_context,
            "duration": content.get('duration', 0),
            "media_type": "audio"
        }
    
    def _enhance_video_context(self, content: Dict[str, Any], user_profile: Dict[str, Any],
                             base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for video messages"""
        return {
            **base_context,
            "duration": content.get('duration', 0),
            "media_type": "video"
        }
    
    def _enhance_postback_context(self, content: Dict[str, Any], user_profile: Dict[str, Any],
                                base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for postback messages"""
        return {
            **base_context,
            "postback_data": content.get('postback_data', ''),
            "interaction_type": "postback"
        }
    
    # Processing methods
    
    async def _process_text_generation(self, selection: ToolSelection, user_profile: Dict[str, Any],
                                     db: AsyncSession) -> str:
        """Process using text generation tools"""
        return await get_ai_response(
            user_message=selection.prompt,
            user_id=user_profile.get('user_id', ''),
            user_profile=user_profile,
            db=db
        )
    
    async def _process_image_analysis(self, selection: ToolSelection, content: Dict[str, Any]) -> str:
        """Process using image analysis tool"""
        image_content = content.get('image_content')
        if not image_content:
            return "ขออภัย ไม่สามารถดาวน์โหลดรูปภาพได้ กรุณาส่งรูปภาพใหม่อีกครั้ง"
        
        return await image_understanding(image_content, selection.prompt)
    
    async def _process_document_analysis(self, selection: ToolSelection, content: Dict[str, Any]) -> str:
        """Process using document analysis tool"""
        document_content = content.get('document_content')
        if not document_content:
            return "ขออภัย ไม่สามารถดาวน์โหลดเอกสารได้ กรุณาส่งไฟล์ใหม่อีกครั้ง"
        
        return await document_understanding(document_content, selection.prompt)
    
    async def _process_location_context(self, selection: ToolSelection, content: Dict[str, Any],
                                      user_profile: Dict[str, Any], db: AsyncSession) -> str:
        """Process location context analysis"""
        return await get_ai_response(
            user_message=selection.prompt,
            user_id=user_profile.get('user_id', ''),
            user_profile=user_profile,
            db=db
        )
    
    async def _process_emotion_analysis(self, selection: ToolSelection, content: Dict[str, Any],
                                      user_profile: Dict[str, Any], db: AsyncSession) -> str:
        """Process emotion analysis for stickers"""
        return await get_ai_response(
            user_message=selection.prompt,
            user_id=user_profile.get('user_id', ''),
            user_profile=user_profile,
            db=db
        )
    
    async def _process_fallback(self, selection: ToolSelection, user_profile: Dict[str, Any],
                              db: AsyncSession) -> str:
        """Process using fallback method"""
        fallback_prompt = f"กรุณาตอบผู้ใช้ชื่อ {user_profile.get('display_name', 'ผู้ใช้')} อย่างสุภาพเป็นภาษาไทย"
        
        return await get_ai_response(
            user_message=fallback_prompt,
            user_id=user_profile.get('user_id', ''),
            user_profile=user_profile,
            db=db
        )

# Global tools selector instance
tools_selector = GeminiToolsSelector()

# Export main functions
async def select_gemini_tool(message_type: str, content: Dict[str, Any], 
                           user_profile: Dict[str, Any], db: AsyncSession) -> ToolSelection:
    """
    Select appropriate Gemini tool for message processing
    
    Args:
        message_type: String representation of message type
        content: Message content and metadata
        user_profile: User profile information
        db: Database session
        
    Returns:
        ToolSelection object
    """
    try:
        msg_type = MessageType(message_type)
    except ValueError:
        msg_type = MessageType.UNKNOWN
    
    return await tools_selector.select_tool(msg_type, content, user_profile, db)

async def process_with_gemini_tool(selection: ToolSelection, content: Dict[str, Any],
                                 user_profile: Dict[str, Any], db: AsyncSession) -> ProcessingResult:
    """
    Process content using selected Gemini tool
    
    Args:
        selection: Tool selection result
        content: Message content
        user_profile: User profile
        db: Database session
        
    Returns:
        ProcessingResult object
    """
    return await tools_selector.process_with_tool(selection, content, user_profile, db)