# Enhanced Message Handler for LINE Bot with Gemini AI Integration
"""
Comprehensive message handler that processes different LINE message types
and routes them to appropriate Gemini AI tools for intelligent responses.

Supported Message Types:
- Text messages
- Sticker messages  
- Image messages
- Video messages
- Audio messages
- Location messages
- Imagemap messages
- Template messages
- Flex messages
- Carousel flex messages
- Quick reply
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession

from linebot.v3.messaging import (
    AsyncMessagingApi, AsyncMessagingApiBlob, TextMessage, StickerMessage,
    ReplyMessageRequest, PushMessageRequest
    # ShowLoadingAnimationRequest removed for compatibility
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent, ImageMessageContent, VideoMessageContent,
    AudioMessageContent, FileMessageContent, LocationMessageContent, 
    StickerMessageContent, PostbackEvent
)

from app.core.config import settings
from app.db.crud import get_or_create_user_status, save_chat_message
from app.db.crud_enhanced import save_chat_to_history, log_system_event
from app.services.gemini_service import (
    get_ai_response, image_understanding, document_understanding, 
    check_gemini_availability
)
from app.services.line_handler_enhanced import (
    get_user_profile_enhanced, send_telegram_notification_enhanced
)
from app.services.ws_manager import manager
from app.utils.timezone import get_thai_time

class MessageHandler:
    """Advanced message handler with Gemini AI integration"""
    
    def __init__(self):
        self.supported_types = {
            'text': self.handle_text_message,
            'image': self.handle_image_message,
            'video': self.handle_video_message,
            'audio': self.handle_audio_message,
            'file': self.handle_file_message,
            'location': self.handle_location_message,
            'sticker': self.handle_sticker_message,
            'postback': self.handle_postback_message,
            'quick_reply': self.handle_quick_reply_message,
            'imagemap': self.handle_imagemap_message,
            'template': self.handle_template_message,
            'flex': self.handle_flex_message,
            'carousel_flex': self.handle_carousel_flex_message
        }
    
    async def process_message(self, event: MessageEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi) -> bool:
        """
        Main entry point for processing all message types
        
        Args:
            event: LINE webhook event
            db: Database session
            line_bot_api: LINE messaging API client
            
        Returns:
            bool: Success status
        """
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            
            # Get user profile
            profile_data = await get_user_profile_enhanced(line_bot_api, user_id)
            
            # Determine message type
            message_type = self._detect_message_type(event)
            
            # Log incoming message
            await log_system_event(
                db=db,
                level="info",
                category="message_handler",
                subcategory="message_received",
                message=f"Processing {message_type} message from {profile_data['display_name']}",
                user_id=user_id,
                details={"message_type": message_type, "profile": profile_data}
            )
            
            # Route to appropriate handler
            if message_type in self.supported_types:
                handler = self.supported_types[message_type]
                success = await handler(event, db, line_bot_api, profile_data)
                
                if success:
                    await log_system_event(
                        db=db, level="info", category="message_handler", 
                        subcategory="message_processed",
                        message=f"Successfully processed {message_type} message",
                        user_id=user_id
                    )
                return success
            else:
                # Unsupported message type
                await self._handle_unsupported_message(event, db, line_bot_api, profile_data, message_type)
                return True
                
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="processing_error",
                message=f"Error processing message: {str(e)}",
                user_id=getattr(event.source, 'user_id', 'unknown')
            )
            return False
    
    def _detect_message_type(self, event: MessageEvent) -> str:
        """Detect the type of incoming message"""
        if hasattr(event, 'message'):
            if isinstance(event.message, TextMessageContent):
                return 'text'
            elif isinstance(event.message, ImageMessageContent):
                return 'image'
            elif isinstance(event.message, VideoMessageContent):
                return 'video'
            elif isinstance(event.message, AudioMessageContent):
                return 'audio'
            elif isinstance(event.message, FileMessageContent):
                return 'file'
            elif isinstance(event.message, LocationMessageContent):
                return 'location'
            elif isinstance(event.message, StickerMessageContent):
                return 'sticker'
        
        if isinstance(event, PostbackEvent):
            return 'postback'
        
        # Check for special message types in message content
        if hasattr(event, 'message') and hasattr(event.message, 'type'):
            msg_type = event.message.type
            if msg_type in ['imagemap', 'template', 'flex']:
                return msg_type
        
        return 'unknown'

    async def handle_text_message(self, event: MessageEvent, db: AsyncSession, 
                                line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle text messages with advanced AI processing"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            message_text = event.message.text
            session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d')}"
            
            # Save user message
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user', 
                message_content=message_text, session_id=session_id,
                extra_data={"profile_data": profile_data, "message_type": "text"}
            )
            await save_chat_message(db, user_id, 'user', message_text)
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": message_text,
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat()
            })
            
            # Special command handling
            if await self._handle_special_commands(message_text, event, db, line_bot_api, profile_data):
                return True
            
            # Get AI response using Gemini
            gemini_available = await check_gemini_availability()
            
            if gemini_available:
                try:
                    # Broadcast loading animation start
                    await manager.broadcast({
                        "type": "bot_response_loading", 
                        "userId": user_id, 
                        "sessionId": session_id
                    })
                    
                    # Show loading animation on LINE
                    await self._show_loading_animation(line_bot_api, user_id)

                    # Enhanced prompt for better context
                    enhanced_prompt = self._enhance_text_prompt(message_text, profile_data)
                    ai_response = await get_ai_response(
                        user_message=enhanced_prompt,
                        user_id=user_id,
                        user_profile=profile_data,
                        db=db
                    )
                    
                    # Reply with AI response
                    await line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=reply_token,
                            messages=[TextMessage(text=ai_response)]
                        )
                    )
                    
                    # Save AI response
                    await save_chat_to_history(
                        db=db, user_id=user_id, message_type='ai_bot',
                        message_content=ai_response, session_id=session_id,
                        extra_data={"ai_powered": True, "gemini_response": True, "original_message": message_text}
                    )
                    await save_chat_message(db, user_id, 'ai_bot', ai_response)
                    
                    # Broadcast AI response to admin panel and signal completion
                    await manager.broadcast({
                        "type": "bot_response_complete", 
                        "userId": user_id, 
                        "message": ai_response, 
                        "sessionId": session_id
                    })
                    
                except Exception as e:
                    # Fallback response
                    fallback_response = "ขออภัย เกิดข้อผิดพลาดในระบบ AI กรุณาลองใหม่อีกครั้ง หรือติดต่อเจ้าหน้าที่"
                    await line_bot_api.reply_message(
                        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=fallback_response)])
                    )
                    
                    await log_system_event(
                        db=db, level="warning", category="gemini", subcategory="ai_fallback",
                        message=f"AI response failed: {str(e)}", user_id=user_id
                    )
            else:
                # AI unavailable fallback
                fallback_response = "สวัสดีค่ะ! ดีใจที่ได้คุยกับคุณนะคะ 😊 หากต้องการคุยกับเจ้าหน้าที่ โปรดพิมพ์ 'ติดต่อเจ้าหน้าที่' ได้เลยค่ะ"
                await line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=fallback_response)])
                )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="text_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_image_message(self, event: MessageEvent, db: AsyncSession,
                                 line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle image messages with AI vision analysis"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            message_id = event.message.id
            session_id = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save image message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_image',
                message_content=f"ส่งรูปภาพ (ID: {message_id})",
                session_id=session_id,
                extra_data={"message_id": message_id, "content_type": "image", "profile_data": profile_data}
            )
            await save_chat_message(db, user_id, 'user', f"[รูปภาพ] ID: {message_id}")

            
            
            
            
            # Show loading animation
            await self._show_loading_animation(line_bot_api, user_id, 5)
            
            try:
                # Download image content
                blob_api = await self._get_blob_api()
                image_content = await blob_api.get_message_content(message_id=message_id)
                
                # Analyze with Gemini Vision
                analysis_prompt = f"กรุณาวิเคราะห์รูปภาพนี้อย่างละเอียดเป็นภาษาไทย สำหรับผู้ใช้ชื่อ {profile_data['display_name']} โดยอธิบายสิ่งที่เห็นในภาพ สีสัน วัตถุต่างๆ และบริบทที่สำคัญ"
                
                ai_response = await image_understanding(image_content, analysis_prompt)
                
                # Reply with analysis
                await line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=f"📸 การวิเคราะห์รูปภาพ:\n\n{ai_response}")]
                    )
                )
                
                # Save AI analysis
                await save_chat_to_history(
                    db=db, user_id=user_id, message_type='ai_image_analysis',
                    message_content=ai_response, session_id=session_id,
                    extra_data={"message_id": message_id, "ai_powered": True, "analysis_type": "image_vision"}
                )
                await save_chat_message(db, user_id, 'ai_bot', f"[วิเคราะห์รูปภาพ] {ai_response}")
                
                # Notify admin
                await send_telegram_notification_enhanced(
                    db=db, notification_type="image_analysis", 
                    title="📸 วิเคราะห์รูปภาพแล้ว",
                    message=f"ผู้ใช้: {profile_data['display_name']}\nผลการวิเคราะห์: {ai_response[:100]}...",
                    user_id=user_id, priority=2,
                    data={"message_id": message_id, "analysis": ai_response}
                )
                
            except Exception as e:
                error_response = "ขออภัย ไม่สามารถวิเคราะห์รูปภาพได้ในขณะนี้ กรุณาลองส่งรูปภาพใหม่อีกครั้ง"
                await line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=error_response)])
                )
                
                await log_system_event(
                    db=db, level="error", category="gemini", subcategory="image_analysis_failed",
                    message=f"Image analysis failed: {str(e)}", user_id=user_id
                )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="image_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_video_message(self, event: MessageEvent, db: AsyncSession,
                                 line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle video messages with metadata analysis"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            message_id = event.message.id
            duration = getattr(event.message, 'duration', 0)
            
            # Save video message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_video',
                message_content=f"ส่งวิดีโอ (ID: {message_id}, ระยะเวลา: {duration}ms)",
                session_id=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"message_id": message_id, "duration": duration, "content_type": "video"}
            )

            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message",
                "userId": user_id,
                "message": f"[วิดีโอ] ID: {message_id} ({duration/1000:.1f}s)",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id,
                "timestamp": thai_time.isoformat(),
                "messageType": "video"
            })
            
            
            
            # Video processing response
            response_text = f"📹 ขอบคุณสำหรับวิดีโอ!\n\nได้รับวิดีโอระยะเวลา {duration/1000:.1f} วินาทีแล้ว"
            
            if duration > 30000:  # > 30 seconds
                response_text += "\n\n⚠️ หมายเหตุ: วิดีโอที่ยาวกว่า 30 วินาทีอาจใช้เวลาในการประมวลผลนานขึ้น"
            
            response_text += "\n\nหากต้องการให้เจ้าหน้าที่ช่วยดูวิดีโอ กรุณาพิมพ์ 'ติดต่อเจ้าหน้าที่'"
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            # Notify admin about video
            await send_telegram_notification_enhanced(
                db=db, notification_type="video_received",
                title="📹 วิดีโอใหม่",
                message=f"ผู้ใช้: {profile_data['display_name']}\nระยะเวลา: {duration/1000:.1f} วินาที",
                user_id=user_id, priority=2,
                data={"message_id": message_id, "duration": duration}
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="video_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_audio_message(self, event: MessageEvent, db: AsyncSession,
                                 line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle audio messages with transcription suggestions"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            message_id = event.message.id
            duration = getattr(event.message, 'duration', 0)
            
            # Save audio message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_audio',
                message_content=f"ส่งข้อความเสียง (ID: {message_id}, ระยะเวลา: {duration}ms)",
                session_id=f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"message_id": message_id, "duration": duration, "content_type": "audio"}
            )

            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message",
                "userId": user_id,
                "message": f"[ข้อความเสียง] ID: {message_id} ({duration/1000:.1f}s)",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id,
                "timestamp": thai_time.isoformat(),
                "messageType": "audio"
            })
            
            
            
            # Audio processing response
            response_text = f"🎵 ขอบคุณสำหรับข้อความเสียง!\n\nได้รับข้อความเสียงระยะเวลา {duration/1000:.1f} วินาทีแล้ว"
            
            if duration > 60000:  # > 1 minute
                response_text += "\n\n💡 เนื่องจากข้อความเสียงค่อนข้างยาว หากสะดวกกรุณาพิมพ์ข้อความสั้นๆ เพื่อความรวดเร็วในการตอบกลับ"
            
            response_text += "\n\nหากต้องการให้เจ้าหน้าที่ฟังข้อความเสียง กรุณาพิมพ์ 'ติดต่อเจ้าหน้าที่'"
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            # Notify admin about audio
            await send_telegram_notification_enhanced(
                db=db, notification_type="audio_received",
                title="🎵 ข้อความเสียงใหม่",
                message=f"ผู้ใช้: {profile_data['display_name']}\nระยะเวลา: {duration/1000:.1f} วินาที",
                user_id=user_id, priority=2,
                data={"message_id": message_id, "duration": duration}
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="audio_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_file_message(self, event: MessageEvent, db: AsyncSession,
                                 line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle file messages with document analysis"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            message_id = event.message.id
            file_name = getattr(event.message, 'file_name', 'unknown_file')
            file_size = getattr(event.message, 'file_size', 0)
            
            # Save file message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_file',
                message_content=f"ส่งไฟล์: {file_name} ({file_size} bytes)",
                session_id=f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"message_id": message_id, "file_name": file_name, "file_size": file_size}
            )

            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message",
                "userId": user_id,
                "message": f"[ไฟล์] {file_name} ({file_size} bytes)",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id,
                "timestamp": thai_time.isoformat(),
                "messageType": "file"
            })
            
            
            
            # Show loading animation
            await self._show_loading_animation(line_bot_api, user_id, 5)
            
            # Check file size and type
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                error_response = "❌ ขออภัย ไฟล์มีขนาดใหญ่เกินไป (เกิน 10MB)\n\nกรุณาส่งไฟล์ที่มีขนาดเล็กกว่า หรือแบ่งเป็นหลายไฟล์"
                await line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=error_response)])
                )
                return True
            
            # Check if it's a supported document type
            supported_extensions = ['.pdf', '.doc', '.docx', '.txt']
            file_extension = '.' + file_name.split('.')[-1].lower() if '.' in file_name else ''
            
            if file_extension not in supported_extensions:
                error_response = f"❌ ประเภทไฟล์ {file_extension} ยังไม่รองรับ\n\nระบบรองรับไฟล์: PDF, DOC, DOCX, TXT\nกรุณาส่งไฟล์ในรูปแบบที่รองรับ"
                await line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=error_response)])
                )
                return True
            
            try:
                # Download and analyze document (PDF only for now)
                if file_extension == '.pdf':
                    blob_api = await self._get_blob_api()
                    file_content = await blob_api.get_message_content(message_id=message_id)
                    
                    analysis_prompt = f"กรุณาสรุปเนื้อหาสำคัญของเอกสารนี้เป็นภาษาไทย สำหรับผู้ใช้ชื่อ {profile_data['display_name']} โดยเน้นประเด็นหลักและข้อมูลที่สำคัญ"
                    
                    ai_response = await document_understanding(file_content, analysis_prompt)
                    
                    response_text = f"📄 การวิเคราะห์เอกสาร: {file_name}\n\n{ai_response}"
                    
                else:
                    # Other document types - basic response
                    response_text = f"📄 ได้รับไฟล์: {file_name}\n\nขนาด: {file_size:,} bytes\nประเภท: {file_extension.upper()}\n\nหากต้องการให้เจ้าหน้าที่ช่วยตรวจสอบไฟล์ กรุณาพิมพ์ 'ติดต่อเจ้าหน้าที่'"
                
                await line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
                )
                
                # Save response
                await save_chat_to_history(
                    db=db, user_id=user_id, message_type='ai_document_analysis',
                    message_content=response_text,
                    session_id=f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    extra_data={"message_id": message_id, "file_name": file_name, "ai_powered": True}
                )
                
                # Notify admin
                await send_telegram_notification_enhanced(
                    db=db, notification_type="document_received",
                    title="📄 เอกสารใหม่",
                    message=f"ผู้ใช้: {profile_data['display_name']}\nไฟล์: {file_name}\nขนาด: {file_size:,} bytes",
                    user_id=user_id, priority=2,
                    data={"message_id": message_id, "file_name": file_name, "file_size": file_size}
                )
                
            except Exception as e:
                error_response = "❌ ขออภัย ไม่สามารถประมวลผลเอกสารได้ในขณะนี้\n\nกรุณาลองส่งใหม่อีกครั้ง หรือติดต่อเจ้าหน้าที่"
                await line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=error_response)])
                )
                
                await log_system_event(
                    db=db, level="error", category="gemini", subcategory="document_analysis_failed",
                    message=f"Document analysis failed: {str(e)}", user_id=user_id
                )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="file_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_location_message(self, event: MessageEvent, db: AsyncSession,
                                    line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle location messages with geographic context"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            
            latitude = event.message.latitude
            longitude = event.message.longitude
            address = getattr(event.message, 'address', 'ไม่ระบุที่อยู่')
            title = getattr(event.message, 'title', 'ตำแหน่งที่ส่ง')
            
            # Save location message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_location',
                message_content=f"ส่งตำแหน่งที่ตั้ง: {title} ({latitude}, {longitude})",
                session_id=f"location_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={
                    "latitude": latitude, "longitude": longitude,
                    "address": address, "title": title
                }
            )

            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message",
                "userId": user_id,
                "message": f"[ตำแหน่ง] {title} ({latitude:.2f}, {longitude:.2f})",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id,
                "timestamp": thai_time.isoformat(),
                "messageType": "location"
            })
            
            
            
            # Create location response with context
            response_text = f"📍 ได้รับตำแหน่งที่ตั้งแล้ว!\n\n"
            response_text += f"🏷️ ชื่อสถานที่: {title}\n"
            response_text += f"📧 ที่อยู่: {address}\n"
            response_text += f"🗺️ พิกัด: {latitude:.6f}, {longitude:.6f}\n\n"
            
            # Add helpful suggestions based on location
            if "hospital" in title.lower() or "โรงพยาบาล" in title:
                response_text += "🏥 เป็นสถานพยาบาล หากต้องการข้อมูลบริการทางการแพทย์ สามารถสอบถามเพิ่มเติมได้"
            elif "school" in title.lower() or "โรงเรียน" in title or "มหาวิทยาลัย" in title:
                response_text += "🏫 เป็นสถาบันการศึกษา หากต้องการข้อมูลด้านการศึกษา สามารถสอบถามเพิ่มเติมได้"
            elif "government" in title.lower() or "ราชการ" in title or "เทศบาล" in title:
                response_text += "🏛️ เป็นหน่วยงานราชการ หากต้องการข้อมูลบริการภาครัฐ สามารถสอบถามเพิ่มเติมได้"
            else:
                response_text += "ขอบคุณสำหรับข้อมูลตำแหน่งที่ตั้ง หากต้องการความช่วยเหลือเพิ่มเติม สามารถสอบถามได้เสมอ"
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            # Notify admin about location sharing
            await send_telegram_notification_enhanced(
                db=db, notification_type="location_shared",
                title="📍 แชร์ตำแหน่งที่ตั้ง",
                message=f"ผู้ใช้: {profile_data['display_name']}\nสถานที่: {title}\nที่อยู่: {address}",
                user_id=user_id, priority=2,
                data={"latitude": latitude, "longitude": longitude, "address": address}
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="location_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_sticker_message(self, event: MessageEvent, db: AsyncSession,
                                   line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle sticker messages with emotional context"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            
            package_id = event.message.package_id
            sticker_id = event.message.sticker_id
            
            # Save sticker message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_sticker',
                message_content=f"ส่งสติกเกอร์ (Package: {package_id}, ID: {sticker_id})",
                session_id=f"sticker_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"package_id": package_id, "sticker_id": sticker_id}
            )

            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message",
                "userId": user_id,
                "message": f"[สติกเกอร์] Package: {package_id}, ID: {sticker_id}",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id,
                "timestamp": thai_time.isoformat(),
                "messageType": "sticker"
            })
            
            
            
            # Analyze sticker emotion and respond appropriately
            sticker_response = await self._analyze_sticker_emotion(package_id, sticker_id)
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=sticker_response)])
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="sticker_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_postback_message(self, event: PostbackEvent, db: AsyncSession,
                                    line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle postback events from interactive elements"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            postback_data = event.postback.data
            
            # Parse postback data
            try:
                data_dict = json.loads(postback_data) if postback_data.startswith('{') else {"action": postback_data}
            except:
                data_dict = {"action": postback_data}
            
            # Save postback event
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_postback',
                message_content=f"Postback: {postback_data}",
                session_id=f"postback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data=data_dict
            )

            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message",
                "userId": user_id,
                "message": f"[Postback] {postback_data}",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id,
                "timestamp": thai_time.isoformat(),
                "messageType": "postback"
            })
            
            
            
            # Handle different postback actions
            response_text = await self._handle_postback_action(data_dict, profile_data)
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="postback_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_quick_reply_message(self, event: MessageEvent, db: AsyncSession,
                                       line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle quick reply responses"""
        # Quick replies are processed as regular text messages with postback data
        return await self.handle_text_message(event, db, line_bot_api, profile_data)

    async def handle_imagemap_message(self, event: MessageEvent, db: AsyncSession,
                                    line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle imagemap interactive messages"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            
            # Save imagemap message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_imagemap',
                message_content=f"ส่ง Imagemap",
                session_id=f"imagemap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"content_type": "imagemap"}
            )
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": f"[Imagemap]",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat(),
                "messageType": "imagemap"
            })
            
            # Save imagemap message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_imagemap',
                message_content=f"ส่ง Imagemap",
                session_id=f"imagemap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"content_type": "imagemap"}
            )
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": f"[Imagemap]",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat(),
                "messageType": "imagemap"
            })
            
            response_text = "🗺️ ขอบคุณสำหรับการใช้งาน Imagemap!\n\nหากต้องการความช่วยเหลือเพิ่มเติม กรุณาพิมพ์คำถามหรือติดต่อเจ้าหน้าที่"
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="imagemap_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_template_message(self, event: MessageEvent, db: AsyncSession,
                                    line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle template message interactions"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            
            # Save template message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_template',
                message_content=f"ส่ง Template",
                session_id=f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"content_type": "template"}
            )
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": f"[Template]",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat(),
                "messageType": "template"
            })
            
            # Save template message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_template',
                message_content=f"ส่ง Template",
                session_id=f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"content_type": "template"}
            )
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": f"[Template]",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat(),
                "messageType": "template"
            })
            
            response_text = "📋 ขอบคุณสำหรับการใช้งานเทมเพลต!\n\nหากต้องการข้อมูลเพิ่มเติม กรุณาเลือกจากตัวเลือกที่ให้ไว้ หรือพิมพ์คำถาม"
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="template_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_flex_message(self, event: MessageEvent, db: AsyncSession,
                                line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle Flex Message interactions"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            
            # Save flex message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_flex',
                message_content=f"ส่ง Flex Message",
                session_id=f"flex_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"content_type": "flex"}
            )
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": f"[Flex Message]",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat(),
                "messageType": "flex"
            })
            
            # Save flex message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_flex',
                message_content=f"ส่ง Flex Message",
                session_id=f"flex_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"content_type": "flex"}
            )
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": f"[Flex Message]",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat(),
                "messageType": "flex"
            })
            
            response_text = "✨ ขอบคุณสำหรับการใช้งาน Flex Message!\n\nระบบได้รับข้อมูลการใช้งานของคุณแล้ว หากต้องการความช่วยเหลือ กรุณาแจ้งได้เสมอ"
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="flex_handler_error", message=str(e), user_id=user_id
            )
            return False

    async def handle_carousel_flex_message(self, event: MessageEvent, db: AsyncSession,
                                         line_bot_api: AsyncMessagingApi, profile_data: Dict) -> bool:
        """Handle Carousel Flex Message interactions"""
        try:
            user_id = event.source.user_id
            reply_token = event.reply_token
            
            # Save carousel flex message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_carousel_flex',
                message_content=f"ส่ง Carousel Flex Message",
                session_id=f"carousel_flex_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"content_type": "carousel_flex"}
            )
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": f"[Carousel Flex Message]",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat(),
                "messageType": "carousel_flex"
            })
            
            # Save carousel flex message log
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='user_carousel_flex',
                message_content=f"ส่ง Carousel Flex Message",
                session_id=f"carousel_flex_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                extra_data={"content_type": "carousel_flex"}
            )
            
            # Broadcast to admin panel via WebSocket
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "new_message", 
                "userId": user_id, 
                "message": f"[Carousel Flex Message]",
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "sessionId": session_id, 
                "timestamp": thai_time.isoformat(),
                "messageType": "carousel_flex"
            })
            
            response_text = "🎠 ขอบคุณสำหรับการใช้งาน Carousel!\n\nหากต้องการดูข้อมูลเพิ่มเติมในหัวข้อใด กรุณาระบุ หรือติดต่อเจ้าหน้าที่ได้เลย"
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            return True
            
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="message_handler",
                subcategory="carousel_handler_error", message=str(e), user_id=user_id
            )
            return False

    # Helper methods
    
    async def _show_loading_animation(self, line_bot_api: AsyncMessagingApi, user_id: str, seconds: int = 3):
        """Show loading animation พร้อมการกำหนดเวลา"""
        try:
            from linebot.v3.messaging import ShowLoadingAnimationRequest
            
            # Maximum allowed loading time is 60 seconds
            loading_seconds = min(seconds, 60)
            
            loading_request = ShowLoadingAnimationRequest(
                chat_id=user_id,
                loading_seconds=loading_seconds
            )
            await line_bot_api.show_loading_animation(loading_request)
        except Exception as e:
            print(f"Could not show loading animation: {e}")
    
    async def _get_blob_api(self) -> AsyncMessagingApiBlob:
        """Get blob API client for downloading content"""
        from linebot.v3.messaging import AsyncApiClient, Configuration
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        async_api_client = AsyncApiClient(configuration)
        return AsyncMessagingApiBlob(async_api_client)
    
    def _enhance_text_prompt(self, message: str, profile_data: Dict) -> str:
        """Enhance text prompt with user context"""
        enhanced = f"ผู้ใช้ชื่อ {profile_data['display_name']} ถามว่า: {message}\n\n"
        enhanced += "กรุณาตอบอย่างสุภาพเป็นภาษาไทย และให้ข้อมูลที่เป็นประโยชน์"
        return enhanced
    
    async def _handle_special_commands(self, message: str, event: MessageEvent, 
                                     db: AsyncSession, line_bot_api: AsyncMessagingApi, 
                                     profile_data: Dict) -> bool:
        """Handle special commands like admin request"""
        if any(keyword in message.lower() for keyword in ['ติดต่อเจ้าหน้าที่', 'คุยกับแอดมิน', 'admin', 'help']):
            user_id = event.source.user_id
            reply_token = event.reply_token
            
            # Switch to live chat mode
            from app.db.crud import set_live_chat_status
            await set_live_chat_status(db, user_id, True, profile_data['display_name'], profile_data['picture_url'])
            
            response_text = "✅ รับทราบ กำลังโอนสายไปยังเจ้าหน้าที่\n\nกรุณารอสักครู่ เจ้าหน้าที่จะเข้ามาคุยกับคุณในไม่ช้า"
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            )
            
            # Notify admin
            await send_telegram_notification_enhanced(
                db=db, notification_type="chat_request",
                title="🚨 ขอคุยกับเจ้าหน้าที่",
                message=f"ผู้ใช้: {profile_data['display_name']}\nข้อความ: {message}",
                user_id=user_id, priority=3,
                data={"trigger_message": message, "profile": profile_data}
            )
            
            # Broadcast human chat request to admin panel
            thai_time = get_thai_time()
            await manager.broadcast({
                "type": "human_chat_request",
                "userId": user_id,
                "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
                "pictureUrl": profile_data.get('picture_url'),
                "message": message,
                "timestamp": thai_time.isoformat()
            })
            
            return True
        
        return False
    
    async def _analyze_sticker_emotion(self, package_id: str, sticker_id: str) -> str:
        """Analyze sticker emotion and provide appropriate response"""
        # Basic sticker emotion mapping
        happy_stickers = ['1', '2', '3', '4', '144']  # Common happy sticker IDs
        sad_stickers = ['5', '6', '7', '8']  # Common sad sticker IDs
        love_stickers = ['9', '10', '11', '12']  # Common love sticker IDs
        
        if sticker_id in happy_stickers:
            return "😊 ดีใจที่เห็นคุณมีความสุข! มีอะไรให้ช่วยเหลือไหมคะ"
        elif sticker_id in sad_stickers:
            return "😔 เห็นใจคุณนะคะ มีอะไรให้ช่วยเหลือไหม หรือต้องการคุยกับเจ้าหน้าที่"
        elif sticker_id in love_stickers:
            return "💖 ขอบคุณมากค่ะ! ยินดีที่ได้ช่วยเหลือคุณ"
        else:
            return "😄 ขอบคุณสำหรับสติกเกอร์น่ารัก! มีอะไรให้ช่วยเหลือไหมคะ"
    
    async def _handle_postback_action(self, data: Dict, profile_data: Dict) -> str:
        """Handle different postback actions"""
        action = data.get('action', 'unknown')
        
        if action == 'view_services':
            return "📋 บริการของเรา:\n\n1. ข้อมูลทั่วไป\n2. แบบฟอร์มคำขอ\n3. ติดต่อเจ้าหน้าที่\n\nกรุณาเลือกบริการที่ต้องการ"
        elif action == 'contact_admin':
            return "📞 กำลังติดต่อเจ้าหน้าที่ให้คุณ กรุณารอสักครู่..."
        elif action == 'help':
            return "❓ วิธีใช้งาน:\n\n- พิมพ์คำถาม เพื่อถามข้อมูล\n- ส่งรูปภาพ เพื่อให้วิเคราะห์\n- ส่งไฟล์ เพื่อให้ตรวจสอบ\n- พิมพ์ 'ติดต่อเจ้าหน้าที่' เพื่อคุยกับคน"
        else:
            return f"ขอบคุณสำหรับการใช้งาน {action} หากต้องการความช่วยเหลือเพิ่มเติม กรุณาแจ้งได้เสมอ"
    
    async def _handle_unsupported_message(self, event: MessageEvent, db: AsyncSession,
                                        line_bot_api: AsyncMessagingApi, profile_data: Dict, message_type: str):
        """Handle unsupported message types"""
        user_id = event.source.user_id
        reply_token = event.reply_token
        
        response_text = f"📱 ขออภัย ระบบยังไม่รองรับข้อความประเภท '{message_type}' ในขณะนี้\n\n"
        response_text += "📝 คุณสามารถ:\n"
        response_text += "• ส่งข้อความธรรมดา\n"
        response_text += "• ส่งรูปภาพ\n" 
        response_text += "• ส่งไฟล์ PDF\n"
        response_text += "• แชร์ตำแหน่งที่ตั้ง\n"
        response_text += "• พิมพ์ 'ติดต่อเจ้าหน้าที่' เพื่อคุยกับคน"
        
        await line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
        )
        
        await log_system_event(
            db=db, level="warning", category="message_handler",
            subcategory="unsupported_type",
            message=f"Unsupported message type: {message_type}",
            user_id=user_id
        )

# Global message handler instance
message_handler = MessageHandler()

# Export main function for integration
async def process_line_message(event: MessageEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi) -> bool:
    """
    Main entry point for processing LINE messages
    
    Args:
        event: LINE message event
        db: Database session
        line_bot_api: LINE messaging API client
        
    Returns:
        bool: Processing success status
    """
    return await message_handler.process_message(event, db, line_bot_api)