#!/usr/bin/env python3
"""
Security scanner for checking potential secrets in code
Run before deployment to ensure no sensitive data is exposed
"""

import os
import re
import sys
from pathlib import Path

# Patterns to detect potential secrets
SECRET_PATTERNS = [
    (r'LINE_CHANNEL_SECRET\s*=\s*["\'][^"\']+["\']', 'LINE Channel Secret'),
    (r'LINE_CHANNEL_ACCESS_TOKEN\s*=\s*["\'][^"\']+["\']', 'LINE Access Token'), 
    (r'TELEGRAM_BOT_TOKEN\s*=\s*["\'][^"\']+["\']', 'Telegram Bot Token'),
    (r'["\'][0-9]{10}:[a-zA-Z0-9_-]{35}["\']', 'Telegram Bot Token Pattern'),
    (r'["\'][a-zA-Z0-9+/]{40,}["\']', 'Base64 Encoded Secret'),
    (r'password\s*=\s*["\'][^"\']+["\']', 'Password'),
    (r'secret\s*=\s*["\'][^"\']+["\']', 'Secret'),
    (r'api_key\s*=\s*["\'][^"\']+["\']', 'API Key'),
]

SAFE_PATTERNS = [
    r'os\.getenv\(',
    r'settings\.',
    r'your_.*_here',
    r'example',
    r'test',
    r'dummy'
]

def scan_file(file_path):
    """Scan a single file for potential secrets"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        issues = []
        for pattern, description in SECRET_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Check if it's a safe pattern
                is_safe = any(re.search(safe, match.group(), re.IGNORECASE) 
                             for safe in SAFE_PATTERNS)
                
                if not is_safe:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'file': file_path,
                        'line': line_num,
                        'description': description,
                        'match': match.group()[:50] + '...' if len(match.group()) > 50 else match.group()
                    })
        
        return issues
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
        return []

def main():
    """Main scanner function"""
    print("Scanning for potential secrets...")
    
    # Files to scan
    extensions = ['.py', '.js', '.json', '.yml', '.yaml', '.toml']
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.env', 'venv', 'env'}
    
    issues = []
    scanned_files = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                scanned_files += 1
                issues.extend(scan_file(file_path))
    
    print(f"Scanned {scanned_files} files")
    
    if issues:
        print(f"\nFound {len(issues)} potential security issues:")
        for issue in issues:
            print(f"  File: {issue['file']}:{issue['line']}")
            print(f"     Issue: {issue['description']}")
            print(f"     Content: {issue['match']}")
            print()
        sys.exit(1)
    else:
        print("No potential secrets found. Safe to deploy!")
        sys.exit(0)

if __name__ == "__main__":
    main()
