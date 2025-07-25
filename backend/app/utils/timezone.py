"""
Timezone utilities with fallback support
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

# Try to import pytz first, fall back to built-in zoneinfo
try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False

try:
    from zoneinfo import ZoneInfo
    ZONEINFO_AVAILABLE = True
except ImportError:
    ZONEINFO_AVAILABLE = False

# Define Thai timezone offset (UTC+7)
THAI_OFFSET = timedelta(hours=7)
THAI_TZ_NAME = 'Asia/Bangkok'

def get_thai_timezone():
    """
    Get Thai timezone object with fallback support
    
    Priority:
    1. pytz (most compatible)
    2. zoneinfo (Python 3.9+)
    3. Manual timezone with fixed offset (fallback)
    """
    if PYTZ_AVAILABLE:
        return pytz.timezone(THAI_TZ_NAME)
    elif ZONEINFO_AVAILABLE:
        return ZoneInfo(THAI_TZ_NAME)
    else:
        # Fallback to manual timezone (UTC+7)
        return timezone(THAI_OFFSET)

def get_thai_time() -> datetime:
    """Get current time in Thai timezone"""
    thai_tz = get_thai_timezone()
    
    if PYTZ_AVAILABLE:
        return datetime.now(thai_tz)
    elif ZONEINFO_AVAILABLE:
        return datetime.now(thai_tz)
    else:
        # Manual calculation for fallback
        utc_now = datetime.now(timezone.utc)
        return utc_now.astimezone(thai_tz)

def convert_to_thai_time(dt: datetime) -> datetime:
    """
    Convert datetime to Thai timezone
    
    Args:
        dt: datetime object (can be naive or timezone-aware)
        
    Returns:
        datetime object in Thai timezone
    """
    thai_tz = get_thai_timezone()
    
    if PYTZ_AVAILABLE:
        if dt.tzinfo is None:
            # Assume naive datetime is UTC
            utc_time = pytz.utc.localize(dt)
        else:
            utc_time = dt.astimezone(pytz.utc)
        return utc_time.astimezone(thai_tz)
    
    elif ZONEINFO_AVAILABLE:
        if dt.tzinfo is None:
            # Assume naive datetime is UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(thai_tz)
    
    else:
        # Manual fallback
        if dt.tzinfo is None:
            # Assume naive datetime is UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(thai_tz)

def format_thai_time(dt: datetime, format_type: str = 'hm') -> str:
    """
    Format datetime for display
    
    Args:
        dt: datetime object
        format_type: 'hm' for HH:MM, 'hms' for HH:MM:SS, 'full' for full format
        
    Returns:
        Formatted time string
    """
    # Convert to Thai time if not already
    if dt.tzinfo is None:
        dt = convert_to_thai_time(dt)
    elif dt.tzinfo != get_thai_timezone():
        dt = convert_to_thai_time(dt)
    
    if format_type == 'hm':
        return dt.strftime('%H:%M')
    elif format_type == 'hms':
        return dt.strftime('%H:%M:%S')
    elif format_type == 'full':
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return dt.strftime('%H:%M')

def get_timezone_info() -> dict:
    """Get information about available timezone support"""
    return {
        'pytz_available': PYTZ_AVAILABLE,
        'zoneinfo_available': ZONEINFO_AVAILABLE,
        'current_method': 'pytz' if PYTZ_AVAILABLE else 'zoneinfo' if ZONEINFO_AVAILABLE else 'manual',
        'thai_timezone': str(get_thai_timezone()),
        'sample_time': get_thai_time().isoformat()
    }