# Gemini CLI Interaction Guide

This document outlines how the Gemini CLI agent interacts with this project.

## Project Overview
This project appears to be a Line chatbot application, likely built with Python, given the `requirements.txt` and numerous `.py` files. It includes features like user management, forms, and potentially enhanced tracking.

## Key Technologies Identified
- Python
- FastAPI (based on `app/api/routers` structure)
- SQLite (based on `chatbot.db` and `database.py`)
- Line Messaging API (implied by "Line chatbot" and `line_handler.py`)
- HTML/CSS/JS for UI (based on `templates/` and `static/` folders)

## Agent Operating Principles
When working on this project, I will adhere to the following principles:

1.  **Convention Adherence:** I will strive to match existing code style, naming conventions, and architectural patterns found within the project.
2.  **Dependency Verification:** Before introducing new libraries or frameworks, I will check `requirements.txt` or similar configuration files to ensure compatibility and existing usage.
3.  **Test-Driven Changes:** Where applicable, I will prioritize creating or utilizing existing tests to verify changes and prevent regressions.
4.  **Clear Communication:** I will explain my plans and actions concisely, especially for commands that modify the file system or system state.
5.  **Security Focus:** I will ensure all changes adhere to security best practices and avoid introducing vulnerabilities.
6.  **Absolute Paths:** All file operations will use absolute paths, resolved from the project root.

## Common Tasks I Can Assist With
- Bug fixes
- Feature additions
- Code refactoring
- Explaining code sections
- Running tests and linters
- Managing project dependencies
- Database migrations (with caution and user confirmation)

## Integration with Other Agents
This `GEMINI.md` file is also intended to serve as a guide for other AI agents, such as Claude Code, to understand the project context and operating principles. I am ready to receive commands and collaborate on tasks initiated by other agents.

Feel free to ask me to perform any of these tasks or provide further context on the project.