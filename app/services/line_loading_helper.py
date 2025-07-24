# Enhanced Loading Animation Helper for LINE Bot
import asyncio
from typing import Optional
from linebot.v3.messaging import AsyncMessagingApi

class LineLoadingAnimationHelper:
    """Helper class for showing loading animations in LINE chat"""
    
    def __init__(self, line_bot_api: AsyncMessagingApi):
        self.line_bot_api = line_bot_api
        
    async def show_loading_animation(
        self, 
        user_id: str, 
        seconds: int = 3,
        fallback_message: Optional[str] = None
    ) -> bool:
        """
        Show loading animation with multiple approaches
        Returns True if successful, False otherwise
        """
        success = False
        
        # Method 1: Try new ShowLoadingAnimationRequest API
        success = await self._try_loading_animation_api(user_id, seconds)
        
        if not success and fallback_message:
            # Method 2: Send typing indicator message as fallback
            success = await self._try_typing_fallback(user_id, fallback_message, seconds)
            
        return success
    
    async def _try_loading_animation_api(self, user_id: str, seconds: int) -> bool:
        """Try using the official ShowLoadingAnimationRequest API"""
        try:
            from linebot.v3.messaging import ShowLoadingAnimationRequest
            
            # Validate user_id format
            if not user_id or not user_id.startswith('U'):
                print(f"⚠️ Invalid user_id format for loading animation: {user_id}")
                return False
            
            # Maximum allowed loading time is 60 seconds
            loading_seconds = min(max(seconds, 1), 60)
            
            print(f"🔄 Attempting to show loading animation for user {user_id} ({loading_seconds}s)")
            
            loading_request = ShowLoadingAnimationRequest(
                chat_id=user_id,
                loading_seconds=loading_seconds
            )
            
            await self.line_bot_api.show_loading_animation(loading_request)
            print(f"✅ Loading animation shown successfully for user {user_id}")
            return True
            
        except ImportError:
            print("⚠️ ShowLoadingAnimationRequest not available in this LINE SDK version")
            return False
        except Exception as e:
            print(f"⚠️ Loading animation failed for user {user_id}: {e}")
            return False
    
    async def _try_typing_fallback(self, user_id: str, message: str, seconds: int) -> bool:
        """Send a typing indicator message as fallback"""
        try:
            from linebot.v3.messaging import TextMessage, PushMessageRequest
            
            # Send typing indicator message
            typing_message = f"💭 {message}"
            push_request = PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=typing_message)]
            )
            
            await self.line_bot_api.push_message(push_request)
            
            # Wait for the specified duration then delete the message
            asyncio.create_task(self._cleanup_typing_message(user_id, seconds))
            
            print(f"✅ Typing fallback sent for user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Typing fallback failed for user {user_id}: {e}")
            return False
    
    async def _cleanup_typing_message(self, user_id: str, seconds: int):
        """Clean up typing message after delay (if possible)"""
        try:
            await asyncio.sleep(seconds)
            # Note: LINE doesn't allow message deletion, so this is just for timing
            print(f"🔄 Typing period ended for user {user_id}")
        except Exception as e:
            print(f"⚠️ Cleanup task error for user {user_id}: {e}")

# Enhanced Message Handler Integration
async def show_enhanced_loading_animation(
    line_bot_api: AsyncMessagingApi,
    user_id: str,
    context: str = "กำลังประมวลผล",
    seconds: int = 3
) -> bool:
    """
    Enhanced loading animation with multiple fallback strategies
    
    Args:
        line_bot_api: LINE Bot API instance
        user_id: LINE user ID
        context: Context description for the loading
        seconds: Loading duration (1-60 seconds)
    
    Returns:
        bool: True if any loading indication was shown successfully
    """
    helper = LineLoadingAnimationHelper(line_bot_api)
    
    # Define context-specific messages
    context_messages = {
        "กำลังประมวลผล": "กำลังประมวลผลคำถามของคุณ...",
        "กำลังวิเคราะห์": "กำลังวิเคราะห์ข้อมูล...",
        "กำลังส่ง": "กำลังส่งข้อความ...",
        "กำลังค้นหา": "กำลังค้นหาข้อมูล...",
        "default": "กรุณารอสักครู่..."
    }
    
    fallback_message = context_messages.get(context, context_messages["default"])
    
    return await helper.show_loading_animation(
        user_id=user_id,
        seconds=seconds,
        fallback_message=fallback_message
    )

# Debug Helper Functions
def validate_user_id_format(user_id: str) -> dict:
    """Validate LINE user ID format and return diagnostic info"""
    result = {
        "valid": False,
        "format": "unknown",
        "length": len(user_id) if user_id else 0,
        "starts_with_U": False,
        "issues": []
    }
    
    if not user_id:
        result["issues"].append("User ID is empty or None")
        return result
    
    result["starts_with_U"] = user_id.startswith('U')
    result["length"] = len(user_id)
    
    if not user_id.startswith('U'):
        result["issues"].append("User ID should start with 'U'")
    
    if len(user_id) != 33:  # Standard LINE user ID length
        result["issues"].append(f"User ID length should be 33, got {len(user_id)}")
    
    # Check for valid characters (alphanumeric)
    if not user_id.replace('-', '').replace('_', '').isalnum():
        result["issues"].append("User ID contains invalid characters")
    
    result["valid"] = len(result["issues"]) == 0
    result["format"] = "LINE User ID" if result["valid"] else "Invalid"
    
    return result

def print_loading_animation_debug(user_id: str, success: bool, error: Optional[str] = None):
    """Print debug information for loading animation attempts"""
    print("\n" + "="*60)
    print("🔍 LOADING ANIMATION DEBUG INFO")
    print("="*60)
    
    validation = validate_user_id_format(user_id)
    
    print(f"👤 User ID: {user_id}")
    print(f"✅ Valid Format: {validation['valid']}")
    print(f"📏 Length: {validation['length']} (expected: 33)")
    print(f"🔤 Starts with 'U': {validation['starts_with_U']}")
    
    if validation["issues"]:
        print("⚠️ Issues found:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    
    print(f"🎯 Animation Success: {'✅ YES' if success else '❌ NO'}")
    
    if error:
        print(f"❌ Error: {error}")
    
    if not success:
        print("\n🔧 TROUBLESHOOTING SUGGESTIONS:")
        print("  1. Check if user_id starts with 'U' (LINE User ID)")
        print("  2. Verify LINE Channel Access Token permissions")
        print("  3. Check if user has blocked the bot")
        print("  4. Try fallback typing indicator instead")
        print("  5. Update LINE Bot SDK to latest version")
    
    print("="*60)

console.log('✅ Enhanced LINE Loading Animation Helper loaded');
