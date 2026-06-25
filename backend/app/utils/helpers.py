"""
Helper functions for the application.
"""
from __future__ import annotations

import os

def load_prompt(relative_path: str, default: str = "") -> str:
    """
    Load prompt content from a file relative to the project root.
    Example: load_prompt("prompts/system/base_system.md", "Default prompt")
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        full_path = os.path.join(project_root, relative_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
    except Exception:
        pass
    return default
