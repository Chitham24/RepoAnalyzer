"""
Execution flow builder for RepoAnalyzer.
Builds high-level execution flows from entry points through the system.
"""
from typing import Dict, List, Set
from collections import defaultdict


class ExecutionFlow:
    """Represents a high-level execution flow."""
    
    def __init__(self):
        self.stages: List[Dict[str, any]] = []
        self.connections: List[Dict[str, str]] = []
    
    def add_stage(self, stage_id: str, stage_type: str, components: List[str], description: str = ""):
        """
        Add a stage to the execution flow.
        
        Args:
            stage_id: Unique identifier for the stage
            stage_type: Type of stage (e.g., 'entry', 'backend', 'database')
            components: List of files/modules in this stage
            description: Optional description
        """
        self.stages.append({
            "id": stage_id,
            "type": stage_type,
            "components": components,
            "description": description,
        })
    
    def add_connection(self, from_stage: str, to_stage: str, label: str = ""):
        """
        Add a connection between stages.
        
        Args:
            from_stage: Source stage ID
            to_stage: Target stage ID
            label: Optional label for the connection
        """
        self.connections.append({
            "from": from_stage,
            "to": to_stage,
            "label": label,
        })
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert flow to dictionary representation.
        
        Returns:
            Dictionary with stages and connections
        """
        return {
            "stages": self.stages,
            "connections": self.connections,
        }


def _identify_backend_components(
    folder_summaries: List[Dict[str, str]],
    frameworks: List[str]
) -> List[str]:
    """Identify backend components from folder summaries."""
    backend_components = []
    
    for summary in folder_summaries:
        role = summary.get("role", "")
        folder = summary.get("folder", "")
        
        # Check if folder is backend-related
        if role in ["backend", "api", "services"]:
            backend_components.append(folder)
    
    return backend_components


def _identify_database_components(
    folder_summaries: List[Dict[str, str]],
    databases: List[str]
) -> List[str]:
    """Identify database-related components."""
    db_components = []
    
    for summary in folder_summaries:
        role = summary.get("role", "")
        folder = summary.get("folder", "")
        
        # Check if folder is database-related
        if role in ["database", "models"]:
            db_components.append(folder)
    
    # Add detected databases
    db_components.extend(databases)
    
    return db_components


def _identify_frontend_components(folder_summaries: List[Dict[str, str]]) -> List[str]:
    """Identify frontend components."""
    frontend_components = []
    
    for summary in folder_summaries:
        role = summary.get("role", "")
        folder = summary.get("folder", "")
        
        if role in ["frontend", "client", "ui"]:
            frontend_components.append(folder)
    
    return frontend_components


def _identify_middleware_components(folder_summaries: List[Dict[str, str]]) -> List[str]:
    """Identify middleware/utility components."""
    middleware_components = []
    
    for summary in folder_summaries:
        role = summary.get("role", "")
        folder = summary.get("folder", "")
        
        if role in ["middleware", "utils", "utilities", "scripts"]:
            middleware_components.append(folder)
    
    return middleware_components


def build_execution_flow(
    entrypoints: Dict[str, List[Dict[str, str]]],
    folder_summaries: List[Dict[str, str]],
    frameworks: List[str],
    databases: List[str],
    infrastructure: List[str]
) -> ExecutionFlow:
    """
    Build a high-level execution flow for the repository.
    
    Args:
        entrypoints: Detected entry points from analysis
        folder_summaries: Folder summaries with roles
        frameworks: Detected frameworks
        databases: Detected databases
        infrastructure: Detected infrastructure tools
        
    Returns:
        ExecutionFlow object representing the high-level flow
    """
    flow = ExecutionFlow()
    
    # Stage 1: Entry Points
    entry_files = [e["path"] for e in entrypoints.get("application_files", [])]
    framework_entries = [e["path"] for e in entrypoints.get("framework_entrypoints", [])]
    all_entries = entry_files + framework_entries
    
    if all_entries:
        flow.add_stage(
            stage_id="entry",
            stage_type="entry_point",
            components=all_entries[:5],  # Limit to top 5
            description="Application entry points"
        )
    
    # Stage 2: Frontend (if exists)
    frontend_components = _identify_frontend_components(folder_summaries)
    if frontend_components:
        flow.add_stage(
            stage_id="frontend",
            stage_type="frontend",
            components=frontend_components,
            description="Frontend/UI layer"
        )
        
        # Connect entry to frontend if web framework detected
        if all_entries and any(fw in ["React", "Vue", "Angular", "Next.js", "Svelte"] for fw in frameworks):
            flow.add_connection("entry", "frontend", "Renders UI")
    
    # Stage 3: Backend/API
    backend_components = _identify_backend_components(folder_summaries, frameworks)
    if backend_components:
        flow.add_stage(
            stage_id="backend",
            stage_type="backend",
            components=backend_components,
            description="Backend services and APIs"
        )
        
        # Connect entry or frontend to backend
        if frontend_components:
            flow.add_connection("frontend", "backend", "API calls")
        elif all_entries:
            flow.add_connection("entry", "backend", "Processes requests")
    
    # Stage 4: Middleware/Utils (if significant)
    middleware_components = _identify_middleware_components(folder_summaries)
    if middleware_components and len(middleware_components) >= 2:
        flow.add_stage(
            stage_id="middleware",
            stage_type="middleware",
            components=middleware_components,
            description="Middleware and utilities"
        )
        
        if backend_components:
            flow.add_connection("backend", "middleware", "Uses utilities")
    
    # Stage 5: Database
    db_components = _identify_database_components(folder_summaries, databases)
    if db_components:
        flow.add_stage(
            stage_id="database",
            stage_type="database",
            components=db_components,
            description="Data persistence layer"
        )
        
        # Connect backend to database
        if backend_components:
            flow.add_connection("backend", "database", "Data operations")
        elif all_entries:
            flow.add_connection("entry", "database", "Data operations")
    
    # Stage 6: External Services (if infrastructure suggests it)
    external_services = []
    
    # Check for Docker, K8s, or cloud infrastructure
    if any(infra in ["Docker", "Kubernetes"] for infra in infrastructure):
        external_services.append("Container orchestration")
    
    # Check for message queues or caching in databases
    if "Redis" in databases:
        external_services.append("Redis (caching/queue)")
    
    if "Elasticsearch" in databases:
        external_services.append("Elasticsearch (search)")
    
    if external_services:
        flow.add_stage(
            stage_id="external",
            stage_type="external_services",
            components=external_services,
            description="External services and infrastructure"
        )
        
        if backend_components:
            flow.add_connection("backend", "external", "External calls")
    
    return flow