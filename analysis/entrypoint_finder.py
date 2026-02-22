"""
Entrypoint finder for RepoAnalyzer.
Identifies application entry points in various languages and frameworks.
"""
from typing import Dict, List
import re


# Entry point file patterns
ENTRYPOINT_FILES = {
    "Python": ["main.py", "app.py", "wsgi.py", "asgi.py", "run.py", "__main__.py"],
    "JavaScript": ["index.js", "server.js", "app.js", "main.js"],
    "TypeScript": ["index.ts", "server.ts", "app.ts", "main.ts"],
    "Go": ["main.go"],
    "Java": ["Main.java", "Application.java"],
    "Rust": ["main.rs"],
}

# Framework-specific patterns to look for in code
FRAMEWORK_ENTRYPOINT_PATTERNS = {
    "Flask": [
        r"app\s*=\s*Flask\(",
        r"@app\.route\(",
        r"if\s+__name__\s*==\s*['\"]__main__['\"].*app\.run\(",
    ],
    "FastAPI": [
        r"app\s*=\s*FastAPI\(",
        r"@app\.get\(",
        r"@app\.post\(",
        r"uvicorn\.run\(",
    ],
    "Django": [
        r"DJANGO_SETTINGS_MODULE",
        r"from\s+django\.core\.wsgi\s+import\s+get_wsgi_application",
        r"from\s+django\.core\.asgi\s+import\s+get_asgi_application",
    ],
    "Express": [
        r"express\(\)",
        r"app\.listen\(",
        r"const\s+app\s*=\s*express\(",
        r"var\s+app\s*=\s*express\(",
    ],
    "NestJS": [
        r"NestFactory\.create",
        r"@Module\(",
        r"bootstrap\(\)",
    ],
}

# Docker entrypoint patterns
DOCKER_PATTERNS = {
    "CMD": r"CMD\s+\[",
    "ENTRYPOINT": r"ENTRYPOINT\s+\[",
}


def _check_framework_patterns(content: str, framework: str) -> bool:
    """Check if content matches framework-specific patterns."""
    if framework not in FRAMEWORK_ENTRYPOINT_PATTERNS:
        return False
    
    patterns = FRAMEWORK_ENTRYPOINT_PATTERNS[framework]
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    
    return False


def _extract_docker_entrypoints(content: str) -> List[str]:
    """Extract CMD and ENTRYPOINT from Dockerfile."""
    entrypoints = []
    
    for line in content.split("\n"):
        line = line.strip()
        
        # Check for CMD
        if line.startswith("CMD"):
            entrypoints.append(line)
        
        # Check for ENTRYPOINT
        if line.startswith("ENTRYPOINT"):
            entrypoints.append(line)
    
    return entrypoints


def find_entrypoints(files: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """
    Find application entry points in the repository.
    
    Args:
        files: List of file objects with 'path', 'extension', 'content' keys
        
    Returns:
        Dictionary categorizing found entry points by type
    """
    result = {
        "application_files": [],
        "framework_entrypoints": [],
        "docker_entrypoints": [],
    }
    
    for file_obj in files:
        path = file_obj.get("path", "")
        content = file_obj.get("content", "")
        filename = path.split("/")[-1] if "/" in path else path
        
        # Check for standard entrypoint files
        for language, entrypoint_files in ENTRYPOINT_FILES.items():
            if filename in entrypoint_files:
                result["application_files"].append({
                    "path": path,
                    "type": language,
                    "filename": filename,
                })
        
        # Check for framework-specific patterns
        for framework in FRAMEWORK_ENTRYPOINT_PATTERNS.keys():
            if _check_framework_patterns(content, framework):
                result["framework_entrypoints"].append({
                    "path": path,
                    "framework": framework,
                })
        
        # Check for Docker entrypoints
        if filename == "Dockerfile" or "Dockerfile" in path:
            docker_entries = _extract_docker_entrypoints(content)
            if docker_entries:
                for entry in docker_entries:
                    result["docker_entrypoints"].append({
                        "path": path,
                        "command": entry,
                    })
    
    # Remove duplicates while preserving order
    result["application_files"] = list({f["path"]: f for f in result["application_files"]}.values())
    result["framework_entrypoints"] = list({f["path"]: f for f in result["framework_entrypoints"]}.values())
    
    return result