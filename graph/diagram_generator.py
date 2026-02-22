"""
Mermaid diagram generator for RepoAnalyzer.
Converts graphs and flows into Mermaid diagram syntax.
"""
from typing import Dict, List
from graph.dependency_graph import DependencyGraph
from graph.flow_builder import ExecutionFlow


def _sanitize_node_id(node_id: str) -> str:
    """
    Sanitize node ID for Mermaid syntax.
    
    Args:
        node_id: Original node identifier
        
    Returns:
        Sanitized identifier safe for Mermaid
    """
    # Replace special characters with underscores
    sanitized = node_id.replace("/", "_").replace(".", "_").replace("-", "_").replace(" ", "_")
    # Remove any remaining special characters
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    return sanitized


def _truncate_label(label: str, max_length: int = 30) -> str:
    """Truncate label to max length."""
    if len(label) <= max_length:
        return label
    return label[:max_length-3] + "..."


def generate_dependency_diagram(graph: DependencyGraph, max_nodes: int = 20) -> str:
    """
    Generate Mermaid diagram for dependency graph.
    
    Args:
        graph: DependencyGraph object
        max_nodes: Maximum number of nodes to include
        
    Returns:
        Mermaid diagram syntax as string
    """
    lines = ["graph TD"]
    
    # Get all nodes and limit if needed
    all_nodes = graph.get_all_nodes()
    
    if len(all_nodes) > max_nodes:
        # Prioritize nodes with most connections
        node_importance = {}
        for node in all_nodes:
            upstream = len(graph.get_upstream(node))
            downstream = len(graph.get_downstream(node))
            node_importance[node] = upstream + downstream
        
        # Sort by importance and take top nodes
        sorted_nodes = sorted(node_importance.items(), key=lambda x: x[1], reverse=True)
        nodes_to_include = [n[0] for n in sorted_nodes[:max_nodes]]
    else:
        nodes_to_include = all_nodes
    
    # Add nodes
    node_map = {}
    for node in nodes_to_include:
        node_id = _sanitize_node_id(node)
        node_label = _truncate_label(node.split("/")[-1])  # Use filename only
        node_map[node] = node_id
        lines.append(f"    {node_id}[{node_label}]")
    
    # Add edges
    edges_added = set()
    for node in nodes_to_include:
        node_id = node_map[node]
        for dep in graph.get_upstream(node):
            if dep in node_map:
                dep_id = node_map[dep]
                edge_key = (node_id, dep_id)
                if edge_key not in edges_added:
                    lines.append(f"    {node_id} --> {dep_id}")
                    edges_added.add(edge_key)
    
    # Add styling
    lines.append("")
    lines.append("    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px")
    
    return "\n".join(lines)


def generate_flow_diagram(flow: ExecutionFlow) -> str:
    """
    Generate Mermaid diagram for execution flow.
    
    Args:
        flow: ExecutionFlow object
        
    Returns:
        Mermaid diagram syntax as string
    """
    lines = ["graph LR"]
    
    flow_dict = flow.to_dict()
    stages = flow_dict.get("stages", [])
    connections = flow_dict.get("connections", [])
    
    if not stages:
        return "graph LR\n    Empty[No execution flow detected]"
    
    # Add stages as subgraphs
    for stage in stages:
        stage_id = _sanitize_node_id(stage["id"])
        stage_type = stage.get("type", "")
        description = stage.get("description", "")
        components = stage.get("components", [])
        
        # Create stage node
        stage_label = description if description else stage_id
        lines.append(f"    {stage_id}[\"{stage_label}\"]")
        
        # Add components as notes (limited to 3)
        if components:
            components_text = "<br/>".join([_truncate_label(c, 25) for c in components[:3]])
            if len(components) > 3:
                components_text += f"<br/>... and {len(components) - 3} more"
    
    # Add connections
    for conn in connections:
        from_id = _sanitize_node_id(conn["from"])
        to_id = _sanitize_node_id(conn["to"])
        label = conn.get("label", "")
        
        if label:
            label = _truncate_label(label, 20)
            lines.append(f"    {from_id} -->|{label}| {to_id}")
        else:
            lines.append(f"    {from_id} --> {to_id}")
    
    # Add styling based on stage type
    lines.append("")
    for stage in stages:
        stage_id = _sanitize_node_id(stage["id"])
        stage_type = stage.get("type", "")
        
        if stage_type == "entry_point":
            lines.append(f"    style {stage_id} fill:#e1f5e1,stroke:#4caf50,stroke-width:3px")
        elif stage_type == "frontend":
            lines.append(f"    style {stage_id} fill:#e3f2fd,stroke:#2196f3,stroke-width:2px")
        elif stage_type == "backend":
            lines.append(f"    style {stage_id} fill:#fff3e0,stroke:#ff9800,stroke-width:2px")
        elif stage_type == "database":
            lines.append(f"    style {stage_id} fill:#fce4ec,stroke:#e91e63,stroke-width:2px")
        elif stage_type == "external_services":
            lines.append(f"    style {stage_id} fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px")
        else:
            lines.append(f"    style {stage_id} fill:#f5f5f5,stroke:#757575,stroke-width:2px")
    
    return "\n".join(lines)


def generate_module_diagram(folder_summaries: List[Dict[str, str]], max_modules: int = 15) -> str:
    """
    Generate Mermaid diagram showing module relationships.
    
    Args:
        folder_summaries: List of folder summary dictionaries
        max_modules: Maximum number of modules to include
        
    Returns:
        Mermaid diagram syntax as string
    """
    lines = ["graph TD"]
    
    if not folder_summaries:
        return "graph TD\n    Empty[No modules detected]"
    
    # Limit modules if needed
    modules = folder_summaries[:max_modules]
    
    # Group modules by role
    role_groups = {}
    for summary in modules:
        role = summary.get("role", "misc")
        folder = summary.get("folder", "")
        
        if role not in role_groups:
            role_groups[role] = []
        role_groups[role].append(folder)
    
    # Add modules grouped by role
    for role, folders in role_groups.items():
        role_id = _sanitize_node_id(role)
        
        # Create role container
        lines.append(f"    subgraph {role_id}[{role.upper()}]")
        
        for folder in folders:
            folder_id = _sanitize_node_id(folder)
            folder_label = _truncate_label(folder, 20)
            lines.append(f"        {folder_id}[{folder_label}]")
        
        lines.append("    end")
    
    # Add some common connections based on roles
    backend_modules = [_sanitize_node_id(f) for f in role_groups.get("backend", [])]
    frontend_modules = [_sanitize_node_id(f) for f in role_groups.get("frontend", [])]
    database_modules = [_sanitize_node_id(f) for f in role_groups.get("database", [])]
    
    # Connect frontend to backend
    if frontend_modules and backend_modules:
        lines.append(f"    {frontend_modules[0]} --> {backend_modules[0]}")
    
    # Connect backend to database
    if backend_modules and database_modules:
        lines.append(f"    {backend_modules[0]} --> {database_modules[0]}")
    
    # Add styling
    lines.append("")
    lines.append("    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px")
    
    return "\n".join(lines)