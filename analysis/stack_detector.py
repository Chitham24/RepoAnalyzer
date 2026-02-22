"""
Stack detection for RepoAnalyzer.
Detects frameworks, databases, and infrastructure tools from code and config files.
"""
from typing import Dict, List, Set
import re


# Framework detection patterns
FRAMEWORK_PATTERNS = {
    # Python Backend
    "Flask": {
        "imports": ["flask", "from flask"],
        "files": ["app.py", "wsgi.py"],
        "dependencies": ["flask"],
    },
    "Django": {
        "imports": ["django", "from django"],
        "files": ["manage.py", "settings.py", "wsgi.py"],
        "dependencies": ["django"],
    },
    "FastAPI": {
        "imports": ["fastapi", "from fastapi"],
        "dependencies": ["fastapi"],
    },
    "Tornado": {
        "imports": ["tornado", "from tornado"],
        "dependencies": ["tornado"],
    },
    
    # JavaScript Backend
    "Express": {
        "imports": ["express", "require('express')", "require(\"express\")"],
        "dependencies": ["express"],
    },
    "NestJS": {
        "imports": ["@nestjs", "from '@nestjs"],
        "dependencies": ["@nestjs/core", "@nestjs/common"],
        "files": ["nest-cli.json"],
    },
    "Koa": {
        "imports": ["koa", "require('koa')", "require(\"koa\")"],
        "dependencies": ["koa"],
    },
    "Hapi": {
        "imports": ["@hapi/hapi", "require('@hapi/hapi')"],
        "dependencies": ["@hapi/hapi"],
    },
    
    # Frontend
    "React": {
        "imports": ["react", "from 'react'", "from \"react\""],
        "dependencies": ["react", "react-dom"],
    },
    "Next.js": {
        "files": ["next.config.js", "next.config.ts"],
        "dependencies": ["next"],
    },
    "Vue": {
        "imports": ["vue", "from 'vue'", "from \"vue\""],
        "dependencies": ["vue"],
        "files": ["vue.config.js"],
    },
    "Angular": {
        "imports": ["@angular", "from '@angular"],
        "dependencies": ["@angular/core"],
        "files": ["angular.json"],
    },
    "Svelte": {
        "dependencies": ["svelte"],
        "files": ["svelte.config.js"],
    },
    
    # ML / Data Science
    "PyTorch": {
        "imports": ["torch", "import torch", "from torch"],
        "dependencies": ["torch", "pytorch"],
    },
    "TensorFlow": {
        "imports": ["tensorflow", "import tensorflow", "from tensorflow"],
        "dependencies": ["tensorflow", "tensorflow-gpu"],
    },
    "Scikit-learn": {
        "imports": ["sklearn", "from sklearn"],
        "dependencies": ["scikit-learn"],
    },
}

# Database detection patterns
DATABASE_PATTERNS = {
    "PostgreSQL": {
        "imports": ["psycopg2", "asyncpg", "pg"],
        "dependencies": ["psycopg2", "asyncpg", "pg"],
        "config": ["postgres://", "postgresql://"],
    },
    "MySQL": {
        "imports": ["mysql", "pymysql", "mysqlclient"],
        "dependencies": ["mysql", "pymysql", "mysql-connector"],
        "config": ["mysql://"],
    },
    "SQLite": {
        "imports": ["sqlite3", "import sqlite3"],
        "dependencies": ["sqlite3"],
        "files": [".db", ".sqlite", ".sqlite3"],
    },
    "MongoDB": {
        "imports": ["pymongo", "mongoose", "mongodb"],
        "dependencies": ["pymongo", "mongoose", "mongodb"],
        "config": ["mongodb://"],
    },
    "Redis": {
        "imports": ["redis", "import redis", "ioredis"],
        "dependencies": ["redis", "ioredis"],
        "config": ["redis://"],
    },
    "Elasticsearch": {
        "imports": ["elasticsearch", "from elasticsearch"],
        "dependencies": ["elasticsearch", "@elastic/elasticsearch"],
        "config": ["elasticsearch://"],
    },
}

# Infrastructure detection patterns
INFRA_PATTERNS = {
    "Docker": {
        "files": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore"],
    },
    "Kubernetes": {
        "files": ["k8s/", "kubernetes/", "deployment.yaml", "service.yaml"],
        "extensions": [".yaml", ".yml"],
        "content": ["kind: Deployment", "kind: Service", "apiVersion: apps/v1"],
    },
    "GitHub Actions": {
        "files": [".github/workflows/"],
    },
    "GitLab CI": {
        "files": [".gitlab-ci.yml"],
    },
    "Terraform": {
        "files": [".tf"],
        "extensions": [".tf"],
    },
}


def _check_imports(content: str, patterns: List[str]) -> bool:
    """Check if content contains any import pattern."""
    content_lower = content.lower()
    for pattern in patterns:
        if pattern.lower() in content_lower:
            return True
    return False


def _check_dependencies(file_path: str, content: str, patterns: List[str]) -> bool:
    """Check if dependency file contains any pattern."""
    if "requirements.txt" in file_path:
        for pattern in patterns:
            if pattern.lower() in content.lower():
                return True
    
    if "pyproject.toml" in file_path:
        for pattern in patterns:
            if pattern.lower() in content.lower():
                return True
    
    if "package.json" in file_path:
        for pattern in patterns:
            if f'"{pattern}"' in content or f"'{pattern}'" in content:
                return True
    
    return False


def detect_frameworks(files: List[Dict[str, str]]) -> List[str]:
    """
    Detect frameworks used in the repository.
    
    Args:
        files: List of file objects with 'path', 'extension', 'content' keys
        
    Returns:
        List of detected framework names
    """
    detected = set()
    
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for file_obj in files:
            path = file_obj.get("path", "")
            content = file_obj.get("content", "")
            
            # Check imports
            if "imports" in patterns and _check_imports(content, patterns["imports"]):
                detected.add(framework)
                break
            
            # Check dependency files
            if "dependencies" in patterns and _check_dependencies(path, content, patterns["dependencies"]):
                detected.add(framework)
                break
            
            # Check specific files
            if "files" in patterns:
                for file_pattern in patterns["files"]:
                    if file_pattern in path:
                        detected.add(framework)
                        break
    
    return sorted(list(detected))


def detect_databases(files: List[Dict[str, str]]) -> List[str]:
    """
    Detect databases used in the repository.
    
    Args:
        files: List of file objects with 'path', 'extension', 'content' keys
        
    Returns:
        List of detected database names
    """
    detected = set()
    
    for database, patterns in DATABASE_PATTERNS.items():
        for file_obj in files:
            path = file_obj.get("path", "")
            content = file_obj.get("content", "")
            
            # Check imports
            if "imports" in patterns and _check_imports(content, patterns["imports"]):
                detected.add(database)
                break
            
            # Check dependencies
            if "dependencies" in patterns and _check_dependencies(path, content, patterns["dependencies"]):
                detected.add(database)
                break
            
            # Check config strings
            if "config" in patterns:
                for config_pattern in patterns["config"]:
                    if config_pattern in content:
                        detected.add(database)
                        break
            
            # Check file extensions
            if "files" in patterns:
                for file_pattern in patterns["files"]:
                    if path.endswith(file_pattern):
                        detected.add(database)
                        break
    
    return sorted(list(detected))


def detect_infrastructure(files: List[Dict[str, str]]) -> List[str]:
    """
    Detect infrastructure and DevOps tools used in the repository.
    
    Args:
        files: List of file objects with 'path', 'extension', 'content' keys
        
    Returns:
        List of detected infrastructure tool names
    """
    detected = set()
    
    for tool, patterns in INFRA_PATTERNS.items():
        for file_obj in files:
            path = file_obj.get("path", "")
            content = file_obj.get("content", "")
            
            # Check specific files
            if "files" in patterns:
                for file_pattern in patterns["files"]:
                    if file_pattern in path:
                        detected.add(tool)
                        break
            
            # Check extensions
            if "extensions" in patterns:
                for ext in patterns["extensions"]:
                    if path.endswith(ext):
                        # If content patterns exist, check them too
                        if "content" in patterns:
                            for content_pattern in patterns["content"]:
                                if content_pattern in content:
                                    detected.add(tool)
                                    break
                        else:
                            detected.add(tool)
                        break
    
    return sorted(list(detected))