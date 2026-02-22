"""
Language detection for RepoAnalyzer.
Maps file extensions to programming languages and provides statistics.
"""
from typing import Dict, List
from collections import defaultdict


# Extension to language mapping
EXTENSION_TO_LANGUAGE = {
    # Python
    ".py": "Python",
    ".pyx": "Python",
    ".pyi": "Python",
    
    # JavaScript / TypeScript
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    
    # Java
    ".java": "Java",
    
    # Go
    ".go": "Go",
    
    # Rust
    ".rs": "Rust",
    
    # C / C++
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".hh": "C++",
    ".hxx": "C++",
    
    # C#
    ".cs": "C#",
    
    # Web
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SCSS",
    ".less": "CSS",
    
    # Shell
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    
    # Config / Data
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
    ".toml": "TOML",
    
    # Ruby
    ".rb": "Ruby",
    
    # PHP
    ".php": "PHP",
    
    # Swift
    ".swift": "Swift",
    
    # Kotlin
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    
    # Scala
    ".scala": "Scala",
    
    # R
    ".r": "R",
    ".R": "R",
    
    # SQL
    ".sql": "SQL",
    
    # Markdown
    ".md": "Markdown",
    ".markdown": "Markdown",
}


def detect_language(file_path: str) -> str:
    """
    Detect programming language from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name or "Unknown"
    """
    # Extract extension
    if "." not in file_path:
        return "Unknown"
    
    extension = "." + file_path.rsplit(".", 1)[-1]
    extension_lower = extension.lower()
    
    return EXTENSION_TO_LANGUAGE.get(extension_lower, "Unknown")


def get_repo_language_stats(files: List[Dict[str, str]]) -> Dict[str, any]:
    """
    Calculate language statistics for a repository.
    
    Args:
        files: List of file objects with 'path', 'extension', 'content' keys
        
    Returns:
        Dictionary with language counts, percentages, and primary language
    """
    language_counts = defaultdict(int)
    language_lines = defaultdict(int)
    total_files = 0
    
    for file_obj in files:
        path = file_obj.get("path", "")
        content = file_obj.get("content", "")
        
        language = detect_language(path)
        
        if language != "Unknown":
            language_counts[language] += 1
            # Count non-empty lines
            lines = len([line for line in content.split("\n") if line.strip()])
            language_lines[language] += lines
            total_files += 1
    
    if total_files == 0:
        return {
            "languages": {},
            "primary_language": None,
            "total_files": 0,
        }
    
    # Calculate percentages
    languages = {}
    for lang, count in language_counts.items():
        languages[lang] = {
            "files": count,
            "lines": language_lines[lang],
            "percentage": round((count / total_files) * 100, 2),
        }
    
    # Sort by file count to find primary language
    primary_language = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else None
    
    return {
        "languages": dict(sorted(languages.items(), key=lambda x: x[1]["files"], reverse=True)),
        "primary_language": primary_language,
        "total_files": total_files,
    }