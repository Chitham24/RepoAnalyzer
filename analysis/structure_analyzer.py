"""
Structure analyzer for RepoAnalyzer.
Classifies repository folders based on their content and naming patterns.
"""
from typing import Dict, List, Set
from collections import defaultdict


# Folder name patterns for classification
FOLDER_PATTERNS = {
    "frontend": {
        "names": ["frontend", "client", "web", "ui", "app", "public", "static", "assets"],
        "frameworks": ["components", "pages", "views", "styles", "hooks"],
    },
    "backend": {
        "names": ["backend", "server", "api", "services", "core", "src/api", "app/api"],
        "frameworks": ["routes", "controllers", "models", "middleware", "handlers"],
    },
    "config": {
        "names": ["config", "configuration", "settings", "env"],
    },
    "infrastructure": {
        "names": ["infra", "infrastructure", "deploy", "deployment", "k8s", "kubernetes", "docker", ".github", ".gitlab"],
    },
    "scripts": {
        "names": ["scripts", "bin", "tools", "utils", "utilities"],
    },
    "tests": {
        "names": ["tests", "test", "__tests__", "spec", "specs"],
    },
    "docs": {
        "names": ["docs", "documentation", "doc"],
    },
    "database": {
        "names": ["database", "db", "migrations", "seeds", "fixtures"],
    },
}

# File type indicators
FRONTEND_EXTENSIONS = {".jsx", ".tsx", ".vue", ".svelte", ".html", ".css", ".scss", ".sass"}
BACKEND_EXTENSIONS = {".py", ".go", ".java", ".rs", ".rb", ".php"}
CONFIG_EXTENSIONS = {".yaml", ".yml", ".json", ".toml", ".ini", ".env", ".config"}
SCRIPT_EXTENSIONS = {".sh", ".bash", ".zsh", ".ps1"}


def _get_folder_from_path(path: str) -> str:
    """Extract the top-level folder from a file path."""
    if "/" not in path:
        return ""
    return path.split("/")[0]


def _classify_by_name(folder: str) -> str:
    """Classify folder based on its name."""
    folder_lower = folder.lower()
    
    for category, patterns in FOLDER_PATTERNS.items():
        if "names" in patterns:
            for name_pattern in patterns["names"]:
                if name_pattern in folder_lower:
                    return category
    
    return "misc"


def _classify_by_content(folder: str, files: List[Dict[str, str]]) -> str:
    """Classify folder based on file types and patterns inside it."""
    folder_files = [f for f in files if f.get("path", "").startswith(folder + "/")]
    
    if not folder_files:
        return "misc"
    
    # Count file types
    frontend_count = 0
    backend_count = 0
    config_count = 0
    script_count = 0
    
    # Check for framework-specific patterns
    has_frontend_patterns = False
    has_backend_patterns = False
    
    for file_obj in folder_files:
        path = file_obj.get("path", "")
        extension = "." + path.rsplit(".", 1)[-1] if "." in path else ""
        
        # Count by extension
        if extension in FRONTEND_EXTENSIONS:
            frontend_count += 1
        if extension in BACKEND_EXTENSIONS:
            backend_count += 1
        if extension in CONFIG_EXTENSIONS:
            config_count += 1
        if extension in SCRIPT_EXTENSIONS:
            script_count += 1
        
        # Check framework patterns
        path_lower = path.lower()
        for pattern in FOLDER_PATTERNS["frontend"]["frameworks"]:
            if f"/{pattern}/" in path_lower or path_lower.endswith(f"/{pattern}"):
                has_frontend_patterns = True
        
        for pattern in FOLDER_PATTERNS["backend"]["frameworks"]:
            if f"/{pattern}/" in path_lower or path_lower.endswith(f"/{pattern}"):
                has_backend_patterns = True
    
    # Classify based on content
    if has_frontend_patterns or (frontend_count > backend_count and frontend_count > 2):
        return "frontend"
    
    if has_backend_patterns or (backend_count > frontend_count and backend_count > 2):
        return "backend"
    
    if config_count > len(folder_files) * 0.5:
        return "config"
    
    if script_count > len(folder_files) * 0.5:
        return "scripts"
    
    return "misc"


def classify_folders(files: List[Dict[str, str]]) -> Dict[str, Dict[str, any]]:
    """
    Classify repository folders based on content and naming.
    
    Args:
        files: List of file objects with 'path', 'extension', 'content' keys
        
    Returns:
        Dictionary mapping folder paths to their classification and metadata
    """
    # Extract unique folders
    folders = set()
    folder_files = defaultdict(list)
    
    for file_obj in files:
        path = file_obj.get("path", "")
        folder = _get_folder_from_path(path)
        
        if folder:
            folders.add(folder)
            folder_files[folder].append(file_obj)
    
    # Classify each folder
    classifications = {}
    
    for folder in sorted(folders):
        # Try name-based classification first
        name_classification = _classify_by_name(folder)
        
        # If ambiguous, use content-based classification
        if name_classification == "misc":
            classification = _classify_by_content(folder, files)
        else:
            classification = name_classification
        
        # Count files in folder
        file_count = len([f for f in files if f.get("path", "").startswith(folder + "/")])
        
        classifications[folder] = {
            "role": classification,
            "file_count": file_count,
        }
    
    return classifications