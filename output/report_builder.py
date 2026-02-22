"""
Report builder for RepoAnalyzer.
Assembles all analysis results into a structured report.
"""
from typing import Dict, List, Any


def build_report(
    repo_metadata: Dict[str, Any],
    language_stats: Dict[str, Any],
    frameworks: List[str],
    databases: List[str],
    infrastructure: List[str],
    folder_structure: Dict[str, Dict[str, Any]],
    entrypoints: Dict[str, List[Dict[str, str]]],
    file_summaries: List[Dict[str, str]],
    folder_summaries: List[Dict[str, str]],
    architecture_summary: Dict[str, str],
    execution_flow_summary: Dict[str, str],
    dependency_graph_dict: Dict[str, Any],
    execution_flow_dict: Dict[str, Any],
    dependency_diagram: str,
    flow_diagram: str,
    module_diagram: str
) -> Dict[str, Any]:
    """
    Build a comprehensive repository analysis report.
    
    Args:
        repo_metadata: Repository metadata (owner, repo, branch, description, etc.)
        language_stats: Language statistics from language_detector
        frameworks: Detected frameworks
        databases: Detected databases
        infrastructure: Detected infrastructure tools
        folder_structure: Folder classification results
        entrypoints: Detected entry points
        file_summaries: LLM-generated file summaries
        folder_summaries: LLM-generated folder summaries
        architecture_summary: LLM-generated architecture overview
        execution_flow_summary: LLM-generated execution flow description
        dependency_graph_dict: Dependency graph as dictionary
        execution_flow_dict: Execution flow as dictionary
        dependency_diagram: Mermaid diagram text for dependencies
        flow_diagram: Mermaid diagram text for execution flow
        module_diagram: Mermaid diagram text for modules
        
    Returns:
        Structured report dictionary with all analysis results
    """
    report = {
        "metadata": {
            "repo_name": repo_metadata.get("repo", "Unknown"),
            "owner": repo_metadata.get("owner", "Unknown"),
            "branch": repo_metadata.get("branch", "main"),
            "description": repo_metadata.get("description", ""),
            "language": repo_metadata.get("language", ""),
            "stars": repo_metadata.get("stars", 0),
        },
        
        "overview": {
            "purpose": architecture_summary.get("purpose", ""),
            "architecture": architecture_summary.get("architecture", ""),
            "summary": architecture_summary.get("summary", ""),
        },
        
        "tech_stack": {
            "languages": _format_language_stats(language_stats),
            "frameworks": frameworks,
            "databases": databases,
            "infrastructure": infrastructure,
            "primary_language": language_stats.get("primary_language", "Unknown"),
            "total_files": language_stats.get("total_files", 0),
        },
        
        "structure": {
            "folders": _format_folder_structure(folder_structure),
            "folder_summaries": _format_folder_summaries(folder_summaries),
            "total_folders": len(folder_structure),
        },
        
        "entry_points": {
            "application_files": entrypoints.get("application_files", []),
            "framework_entrypoints": entrypoints.get("framework_entrypoints", []),
            "docker_entrypoints": entrypoints.get("docker_entrypoints", []),
            "total_entrypoints": len(entrypoints.get("application_files", [])) + 
                                len(entrypoints.get("framework_entrypoints", [])),
        },
        
        "execution_flow": {
            "description": execution_flow_summary.get("summary", ""),
            "entry_point": execution_flow_summary.get("entry_point", ""),
            "request_flow": execution_flow_summary.get("request_flow", ""),
            "key_interactions": execution_flow_summary.get("key_interactions", ""),
            "stages": execution_flow_dict.get("stages", []),
            "connections": execution_flow_dict.get("connections", []),
        },
        
        "dependencies": {
            "graph": dependency_graph_dict,
            "total_nodes": len(dependency_graph_dict.get("nodes", [])),
            "total_edges": sum(len(deps) for deps in dependency_graph_dict.get("edges", {}).values()),
        },
        
        "key_insights": {
            "architecture_pattern": _infer_architecture_pattern(
                folder_structure, frameworks, folder_summaries
            ),
            "tech_choices": architecture_summary.get("tech_choices", ""),
            "key_modules": architecture_summary.get("key_modules", ""),
        },
        
        "file_summaries": _format_file_summaries(file_summaries),
        
        "diagrams": {
            "dependency_diagram": dependency_diagram,
            "flow_diagram": flow_diagram,
            "module_diagram": module_diagram,
        },
    }
    
    return report


def _format_language_stats(language_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Format language statistics for report."""
    languages = language_stats.get("languages", {})
    
    formatted = []
    for lang, stats in languages.items():
        formatted.append({
            "language": lang,
            "files": stats.get("files", 0),
            "lines": stats.get("lines", 0),
            "percentage": stats.get("percentage", 0.0),
        })
    
    return formatted


def _format_folder_structure(folder_structure: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format folder structure for report."""
    formatted = []
    
    for folder, info in folder_structure.items():
        formatted.append({
            "folder": folder,
            "role": info.get("role", "misc"),
            "file_count": info.get("file_count", 0),
        })
    
    # Sort by role priority
    role_priority = {
        "backend": 1,
        "frontend": 2,
        "api": 3,
        "database": 4,
        "config": 5,
        "tests": 6,
        "docs": 7,
        "misc": 99,
    }
    
    formatted.sort(key=lambda x: role_priority.get(x["role"], 50))
    
    return formatted


def _format_folder_summaries(folder_summaries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Format folder summaries for report."""
    formatted = []
    
    for summary in folder_summaries:
        formatted.append({
            "folder": summary.get("folder", ""),
            "role": summary.get("role", ""),
            "purpose": summary.get("purpose", ""),
            "key_components": summary.get("key_components", ""),
            "interactions": summary.get("interactions", ""),
            "summary": summary.get("summary", ""),
        })
    
    return formatted


def _format_file_summaries(file_summaries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Format file summaries for report, limited to key files."""
    # Filter out skipped/error files
    valid_summaries = [
        s for s in file_summaries
        if s.get("summary") and 
        not s["summary"].startswith("Error") and 
        not s["summary"].startswith("File skipped")
    ]
    
    # Limit to top 20 files
    formatted = []
    for summary in valid_summaries[:20]:
        formatted.append({
            "path": summary.get("path", ""),
            "language": summary.get("language", ""),
            "purpose": summary.get("purpose", ""),
            "responsibilities": summary.get("responsibilities", ""),
            "dependencies": summary.get("dependencies", ""),
        })
    
    return formatted


def _infer_architecture_pattern(
    folder_structure: Dict[str, Dict[str, Any]],
    frameworks: List[str],
    folder_summaries: List[Dict[str, str]]
) -> str:
    """Infer the likely architecture pattern from structure and frameworks."""
    roles = [info.get("role", "") for info in folder_structure.values()]
    
    # Check for common patterns
    has_frontend = any(role in ["frontend", "client", "ui"] for role in roles)
    has_backend = any(role in ["backend", "api", "services"] for role in roles)
    has_database = any(role in ["database", "models"] for role in roles)
    
    # Pattern detection
    if has_frontend and has_backend:
        if any(fw in ["React", "Vue", "Angular"] for fw in frameworks):
            return "Full-stack web application (Frontend + Backend)"
        return "Client-Server architecture"
    
    if has_backend and has_database:
        if any(fw in ["Flask", "Django", "FastAPI", "Express"] for fw in frameworks):
            return "Backend API service with database"
        return "Backend application"
    
    if has_backend and any(fw in ["Flask", "Django", "FastAPI", "Express"] for fw in frameworks):
        return "Web API/Microservice"
    
    if has_frontend:
        return "Frontend application"
    
    if any(fw in ["PyTorch", "TensorFlow", "Scikit-learn"] for fw in frameworks):
        return "Machine Learning / Data Science project"
    
    return "Modular application"