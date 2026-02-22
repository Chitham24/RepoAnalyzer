"""
Centralized filtering rules for RepoAnalyzer.
Defines rules for ignoring paths and identifying file types.
"""
import os
from typing import Set

# Directories to ignore
IGNORED_DIRECTORIES: Set[str] = {
    ".git",
    ".github",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "coverage",
    ".DS_Store",
}

# Allowed file extensions
ALLOWED_EXTENSIONS: Set[str] = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".r",
    ".m",
    ".sql",
    ".sh",
    ".bash",
    ".yaml",
    ".yml",
    ".json",
    ".xml",
    ".md",
    ".txt",
    ".rst",
    ".toml",
    ".ini",
    ".cfg",
}


def is_ignored_path(path: str) -> bool:
    """
    Check if a path should be ignored based on directory rules.
    
    Args:
        path: File or directory path
        
    Returns:
        True if path should be ignored, False otherwise
    """
    path_parts = path.split("/")
    return any(part in IGNORED_DIRECTORIES for part in path_parts)


def is_allowed_file(path: str) -> bool:
    """
    Check if a file is allowed based on extension rules.
    
    Args:
        path: File path
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    _, ext = os.path.splitext(path)
    return ext.lower() in ALLOWED_EXTENSIONS


def is_binary_file(content: bytes) -> bool:
    """
    Heuristic check for binary content.
    
    Args:
        content: File content as bytes
        
    Returns:
        True if content appears to be binary, False otherwise
    """
    # Check for null bytes (common in binary files)
    if b"\x00" in content:
        return True
    
    # Sample first 8KB for text detection
    sample = content[:8192]
    
    # Count non-text characters
    non_text_chars = sum(1 for byte in sample if byte < 32 and byte not in (9, 10, 13))
    
    # If more than 30% are non-text characters, consider it binary
    if len(sample) > 0 and (non_text_chars / len(sample)) > 0.3:
        return True
    
    return False