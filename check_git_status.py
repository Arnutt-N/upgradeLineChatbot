#!/usr/bin/env python3
"""
Git Status Checker - Shows what files will be tracked vs ignored
"""

import os
import subprocess
from pathlib import Path

def run_git_command(command):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception as e:
        print(f"Error running git command: {e}")
        return []

def check_git_status():
    """Check git status and show tracked vs ignored files"""
    print("GIT STATUS ANALYSIS")
    print("=" * 60)
    
    # Check if we're in a git repository
    if not Path('.git').exists():
        print("Not in a git repository. Run 'git init' first.")
        return
    
    print("\n📊 TRACKED FILES (will be committed):")
    print("-" * 40)
    
    # Get tracked files
    tracked_files = run_git_command("git ls-files")
    if tracked_files and tracked_files[0]:
        for file in sorted(tracked_files):
            print(f"✅ {file}")
    else:
        print("No files are currently tracked.")
    
    print(f"\nTotal tracked files: {len(tracked_files) if tracked_files and tracked_files[0] else 0}")
    
    print("\n🚫 IGNORED FILES (will NOT be committed):")
    print("-" * 40)
    
    # Get ignored files
    ignored_files = run_git_command("git ls-files --others --ignored --exclude-standard")
    if ignored_files and ignored_files[0]:
        # Group by category
        categories = {
            'Python Cache': [],
            'Environment': [],
            'Database': [],
            'Logs': [],
            'IDE': [],
            'Backup': [],
            'Other': []
        }
        
        for file in ignored_files:
            if '__pycache__' in file or file.endswith('.pyc'):
                categories['Python Cache'].append(file)
            elif file.startswith('.env') or 'venv' in file or 'env/' in file:
                categories['Environment'].append(file)
            elif file.endswith('.db') or file.endswith('.log') or 'backup' in file:
                if '.db' in file:
                    categories['Database'].append(file)
                elif '.log' in file:
                    categories['Logs'].append(file)
                else:
                    categories['Backup'].append(file)
            elif '.vscode' in file or '.idea' in file:
                categories['IDE'].append(file)
            else:
                categories['Other'].append(file)
        
        for category, files in categories.items():
            if files:
                print(f"\n{category}:")
                for file in sorted(files)[:10]:  # Show first 10 files
                    print(f"  🚫 {file}")
                if len(files) > 10:
                    print(f"  ... and {len(files) - 10} more files")
    else:
        print("No ignored files found.")
    
    print(f"\nTotal ignored files: {len(ignored_files) if ignored_files and ignored_files[0] else 0}")
    
    print("\n📋 UNTRACKED FILES (not ignored, not tracked):")
    print("-" * 40)
    
    # Get untracked files
    untracked_files = run_git_command("git ls-files --others --exclude-standard")
    if untracked_files and untracked_files[0]:
        for file in sorted(untracked_files)[:20]:  # Show first 20
            print(f"⚠️  {file}")
        if len(untracked_files) > 20:
            print(f"... and {len(untracked_files) - 20} more files")
    else:
        print("No untracked files.")
    
    print(f"\nTotal untracked files: {len(untracked_files) if untracked_files and untracked_files[0] else 0}")

def check_gitignore_effectiveness():
    """Check how effective the .gitignore is"""
    print("\n" + "=" * 60)
    print("📊 GITIGNORE EFFECTIVENESS ANALYSIS")
    print("=" * 60)
    
    # Key files that should be ignored
    should_be_ignored = [
        '.env',
        'chatbot.db',
        '__pycache__',
        'venv/',
        '.vscode/',
        '*.log',
        'backup_before_refactor/',
        'Line.txt'
    ]
    
    print("\n✅ CRITICAL FILES PROPERLY IGNORED:")
    for pattern in should_be_ignored:
        if '*' in pattern:
            # Check for pattern
            files = list(Path('.').rglob(pattern.replace('*', '')))
            if files:
                print(f"  🔒 {pattern} - {len(files)} files ignored")
            else:
                print(f"  ℹ️  {pattern} - no files found")
        else:
            if Path(pattern).exists():
                result = subprocess.run(
                    ['git', 'check-ignore', pattern],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"  🔒 {pattern} - properly ignored")
                else:
                    print(f"  ⚠️  {pattern} - NOT ignored (potential issue)")
            else:
                print(f"  ℹ️  {pattern} - file doesn't exist")
    
    # Important files that should be tracked
    should_be_tracked = [
        'README.md',
        'backend/app/main.py',
        'backend/requirements.txt',
        'frontend/templates/',
        'config/docker-compose.yml',
        '.env.example'
    ]
    
    print("\n✅ IMPORTANT FILES PROPERLY TRACKED:")
    for file_path in should_be_tracked:
        if Path(file_path).exists():
            result = subprocess.run(
                ['git', 'ls-files', file_path],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                print(f"  📁 {file_path} - properly tracked")
            else:
                print(f"  ⚠️  {file_path} - NOT tracked (may need to add)")
        else:
            print(f"  ℹ️  {file_path} - doesn't exist")

def main():
    """Main function"""
    check_git_status()
    check_gitignore_effectiveness()
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATIONS")
    print("=" * 60)
    print("1. Review untracked files and add important ones with 'git add'")
    print("2. Ensure sensitive files (.env, databases) are ignored")
    print("3. Consider adding README.md and documentation files")
    print("4. Use 'git add -A' to add all trackable files")
    print("5. Run 'git status' to see current state")

if __name__ == "__main__":
    main()