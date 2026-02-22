"""
Dependency graph builder for RepoAnalyzer.
Builds file-level dependency graphs based on imports and requires.
"""
from typing import Dict, List, Set
import re
from collections import defaultdict


class DependencyGraph:
    """Represents a file-level dependency graph."""
    
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_edges: Dict[str, Set[str]] = defaultdict(set)
    
    def add_node(self, node: str):
        """Add a node to the graph."""
        self.nodes.add(node)
    
    def add_edge(self, from_node: str, to_node: str):
        """Add a directed edge from one node to another."""
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        self.edges[from_node].add(to_node)
        self.reverse_edges[to_node].add(from_node)
    
    def get_downstream(self, node: str) -> List[str]:
        """
        Get all nodes that depend on this node (downstream dependencies).
        
        Args:
            node: Node identifier
            
        Returns:
            List of downstream node identifiers
        """
        return sorted(list(self.reverse_edges.get(node, set())))
    
    def get_upstream(self, node: str) -> List[str]:
        """
        Get all nodes this node depends on (upstream dependencies).
        
        Args:
            node: Node identifier
            
        Returns:
            List of upstream node identifiers
        """
        return sorted(list(self.edges.get(node, set())))
    
    def get_all_nodes(self) -> List[str]:
        """Get all nodes in the graph."""
        return sorted(list(self.nodes))
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert graph to dictionary representation.
        
        Returns:
            Dictionary with nodes and edges
        """
        return {
            "nodes": sorted(list(self.nodes)),
            "edges": {node: sorted(list(deps)) for node, deps in self.edges.items()},
        }


def _extract_python_imports(content: str) -> List[str]:
    """Extract import statements from Python code."""
    imports = []
    
    # Pattern for: import module
    # Pattern for: from module import ...
    patterns = [
        r"^import\s+([\w.]+)",
        r"^from\s+([\w.]+)\s+import",
    ]
    
    for line in content.split("\n"):
        line = line.strip()
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                module = match.group(1)
                # Get the top-level module
                top_module = module.split(".")[0]
                imports.append(top_module)
                break
    
    return list(set(imports))


def _extract_js_imports(content: str) -> List[str]:
    """Extract import/require statements from JavaScript/TypeScript code."""
    imports = []
    
    # Patterns for:
    # import ... from 'module'
    # require('module')
    # import('module')
    patterns = [
        r"import\s+.*?from\s+['\"]([^'\"]+)['\"]",
        r"require\s*\(['\"]([^'\"]+)['\"]\)",
        r"import\s*\(['\"]([^'\"]+)['\"]\)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Skip relative imports (starting with . or /)
            if not match.startswith(".") and not match.startswith("/"):
                # Get the package name (first part before /)
                package = match.split("/")[0]
                # Remove @ prefix if present
                if package.startswith("@") and "/" in match:
                    package = match.split("/")[0] + "/" + match.split("/")[1]
                imports.append(package)
    
    return list(set(imports))


def _normalize_path(file_path: str) -> str:
    """Normalize file path to module name."""
    # Remove extension
    if "." in file_path:
        file_path = file_path.rsplit(".", 1)[0]
    
    # Replace slashes with dots
    return file_path.replace("/", ".")


def _resolve_import_to_file(import_name: str, all_files: List[str]) -> str:
    """
    Try to resolve an import name to an actual file in the repository.
    
    Args:
        import_name: Import/module name
        all_files: List of all file paths in the repo
        
    Returns:
        Matching file path or None
    """
    # Normalize files
    normalized_files = {_normalize_path(f): f for f in all_files}
    
    # Direct match
    if import_name in normalized_files.values():
        return import_name
    
    # Try normalized match
    if import_name in normalized_files:
        return normalized_files[import_name]
    
    # Try partial match (check if any file path contains the import name)
    for norm_path, orig_path in normalized_files.items():
        if import_name in norm_path or norm_path.endswith(import_name):
            return orig_path
    
    return None


def build_dependency_graph(files: List[Dict[str, str]]) -> DependencyGraph:
    """
    Build a file-level dependency graph from repository files.
    
    Args:
        files: List of file objects with 'path', 'extension', 'content' keys
        
    Returns:
        DependencyGraph object representing file dependencies
    """
    graph = DependencyGraph()
    
    # Get all file paths
    all_file_paths = [f.get("path", "") for f in files]
    
    # Process each file
    for file_obj in files:
        file_path = file_obj.get("path", "")
        content = file_obj.get("content", "")
        
        if not file_path or not content:
            continue
        
        # Add node for this file
        graph.add_node(file_path)
        
        # Detect language and extract imports
        imports = []
        
        if file_path.endswith(".py"):
            imports = _extract_python_imports(content)
        elif file_path.endswith((".js", ".jsx", ".ts", ".tsx")):
            imports = _extract_js_imports(content)
        
        # Resolve imports to actual files
        for import_name in imports:
            resolved_file = _resolve_import_to_file(import_name, all_file_paths)
            if resolved_file and resolved_file != file_path:
                graph.add_edge(file_path, resolved_file)
    
    return graph