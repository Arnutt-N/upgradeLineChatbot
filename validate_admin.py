#!/usr/bin/env python3
"""
HTML/JavaScript Validation Script
ตรวจสอบ syntax error ในไฟล์ admin.html
"""

import re
import sys

def validate_html_js(file_path):
    """ตรวจสอบ HTML/JavaScript syntax"""
    
    print(f"🔍 Validating {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 File size: {len(content)} characters")
        print(f"📄 Line count: {len(content.splitlines())} lines")
        
        # Check for common JavaScript syntax errors
        errors = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for unmatched braces
            if line_stripped.endswith('} else {') and not line_stripped.startswith('//'):
                continue
            
            # Check for standalone closing braces
            if line_stripped == '}' and i > 1:
                prev_line = lines[i-2].strip() if i > 1 else ''
                if prev_line.endswith('}'):
                    errors.append(f"Line {i}: Possible extra closing brace")
            
            # Check for missing semicolons before closing braces
            if line_stripped == '}' and i > 1:
                prev_line = lines[i-2].strip() if i > 1 else ''
                if prev_line and not prev_line.endswith((';', '{', '}', ')', ',')) and not prev_line.startswith('//'):
                    errors.append(f"Line {i-1}: Missing semicolon before closing brace")
            
            # Check for unmatched function declarations
            if 'function ' in line and line.count('(') != line.count(')'):
                errors.append(f"Line {i}: Unmatched parentheses in function declaration")
        
        # Check overall brace balance
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            errors.append(f"Brace mismatch: {open_braces} opening braces, {close_braces} closing braces")
        
        # Check for common JavaScript errors
        if '} else {' in content and '}else{' in content:
            errors.append("Mixed 'else' formatting detected")
        
        # Print results
        if errors:
            print(f"❌ Found {len(errors)} potential issues:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more issues")
        else:
            print("✅ No obvious syntax errors detected")
        
        # Check for specific areas that might cause issues
        print("\n🔍 Checking specific patterns...")
        
        # Look for the area around line 2494
        target_line = 2494
        if len(lines) >= target_line:
            start = max(0, target_line - 10)
            end = min(len(lines), target_line + 10)
            
            print(f"\n📍 Content around line {target_line}:")
            for i in range(start, end):
                marker = ">>> " if i == target_line - 1 else "    "
                print(f"{marker}{i+1:4d}: {lines[i]}")
        
        return len(errors) == 0
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    html_file = "D:/hrProject/upgradeLineChatbot/templates/admin.html"
    
    print("🧪 HTML/JavaScript Syntax Validator")
    print("=" * 50)
    
    is_valid = validate_html_js(html_file)
    
    if is_valid:
        print("\n✅ File appears to be syntactically correct!")
    else:
        print("\n❌ File contains potential syntax errors!")
        print("\n💡 Recommendations:")
        print("   1. Check JavaScript console in browser")
        print("   2. Use a code editor with syntax highlighting")
        print("   3. Validate JavaScript with online tools")
    
    print("\n🌐 Test the page: http://localhost:8000/admin")
