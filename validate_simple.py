#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML/JavaScript Validation Script
ตรวจสอบ syntax error ในไฟล์ admin.html
"""

import re
import sys

def validate_html_js(file_path):
    """ตรวจสอบ HTML/JavaScript syntax"""
    
    print(f"Validating {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"File size: {len(content)} characters")
        print(f"Line count: {len(content.splitlines())} lines")
        
        # Check for common JavaScript syntax errors
        errors = []
        lines = content.splitlines()
        
        # Check overall brace balance
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            errors.append(f"Brace mismatch: {open_braces} opening braces, {close_braces} closing braces")
        
        # Check for specific areas that might cause issues around line 2494
        target_line = 2494
        if len(lines) >= target_line:
            for i in range(max(0, target_line - 5), min(len(lines), target_line + 5)):
                line = lines[i].strip()
                line_num = i + 1
                
                # Check for common syntax issues
                if line == '}' and i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line == '}':
                        errors.append(f"Line {line_num}: Possible extra closing brace")
                
                # Check for function definitions without body
                if 'function' in line and line.endswith('{') and i < len(lines) - 1:
                    next_line = lines[i+1].strip()
                    if next_line == '}':
                        errors.append(f"Line {line_num}: Empty function body")
        
        # Print results
        if errors:
            print(f"Found {len(errors)} potential issues:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("No obvious syntax errors detected")
        
        # Show content around line 2494
        print(f"\nContent around line {target_line}:")
        start = max(0, target_line - 5)
        end = min(len(lines), target_line + 5)
        
        for i in range(start, end):
            marker = ">>> " if i == target_line - 1 else "    "
            print(f"{marker}{i+1:4d}: {lines[i][:80]}")  # Limit line length
        
        return len(errors) == 0
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

if __name__ == "__main__":
    html_file = "D:/hrProject/upgradeLineChatbot/templates/admin.html"
    
    print("HTML/JavaScript Syntax Validator")
    print("=" * 50)
    
    is_valid = validate_html_js(html_file)
    
    if is_valid:
        print("\nFile appears to be syntactically correct!")
    else:
        print("\nFile contains potential syntax errors!")
    
    print("\nTest the page: http://localhost:8000/admin")
