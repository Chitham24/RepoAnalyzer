"""
Output formatter for RepoAnalyzer.
Converts structured report data into user-facing formats (Markdown, JSON).
"""
from typing import Dict, List, Any
import json


def format_markdown(report: Dict[str, Any]) -> str:
    """
    Format report as Markdown.
    
    Args:
        report: Structured report dictionary from report_builder
        
    Returns:
        Markdown-formatted string
    """
    sections = []
    
    # Header
    sections.append(_format_header(report))
    
    # Overview
    sections.append(_format_overview(report))
    
    # Tech Stack
    sections.append(_format_tech_stack(report))
    
    # Architecture
    sections.append(_format_architecture(report))
    
    # Folder Structure
    sections.append(_format_folder_structure(report))
    
    # Entry Points
    sections.append(_format_entry_points(report))
    
    # Execution Flow
    sections.append(_format_execution_flow(report))
    
    # Module Summaries
    sections.append(_format_module_summaries(report))
    
    # Diagrams
    sections.append(_format_diagrams(report))
    
    # Dependencies (optional, can be verbose)
    if report.get("dependencies", {}).get("total_nodes", 0) > 0:
        sections.append(_format_dependencies(report))
    
    return "\n\n".join(sections)


def format_json(report: Dict[str, Any]) -> str:
    """
    Format report as JSON.
    
    Args:
        report: Structured report dictionary from report_builder
        
    Returns:
        JSON-formatted string
    """
    return json.dumps(report, indent=2, ensure_ascii=False)


def _format_header(report: Dict[str, Any]) -> str:
    """Format markdown header section."""
    metadata = report.get("metadata", {})
    tech_stack = report.get("tech_stack", {})
    
    lines = [
        f"# {metadata.get('repo_name', 'Repository')} Analysis Report",
        "",
        f"**Owner:** {metadata.get('owner', 'Unknown')}  ",
        f"**Repository:** {metadata.get('repo_name', 'Unknown')}  ",
        f"**Branch:** {metadata.get('branch', 'main')}  ",
        f"**Primary Language:** {tech_stack.get('primary_language', 'Unknown')}  ",
    ]
    
    if metadata.get("stars", 0) > 0:
        lines.append(f"**Stars:** ⭐ {metadata.get('stars')}  ")
    
    if metadata.get("description"):
        lines.extend(["", f"**Description:** {metadata.get('description')}"])
    
    return "\n".join(lines)


def _format_overview(report: Dict[str, Any]) -> str:
    """Format overview section."""
    overview = report.get("overview", {})
    insights = report.get("key_insights", {})
    
    lines = [
        "## 📋 Overview",
        "",
    ]
    
    if overview.get("purpose"):
        lines.extend([
            "### Purpose",
            overview.get("purpose"),
            "",
        ])
    
    if insights.get("architecture_pattern"):
        lines.extend([
            f"**Architecture Pattern:** {insights.get('architecture_pattern')}",
            "",
        ])
    
    if overview.get("architecture"):
        lines.extend([
            "### Architecture",
            overview.get("architecture"),
            "",
        ])
    
    return "\n".join(lines)


def _format_tech_stack(report: Dict[str, Any]) -> str:
    """Format tech stack section."""
    tech_stack = report.get("tech_stack", {})
    languages = tech_stack.get("languages", [])
    
    lines = [
        "## 🛠️ Technology Stack",
        "",
    ]
    
    # Languages
    if languages:
        lines.append("### Languages")
        lines.append("")
        lines.append("| Language | Files | Lines | Percentage |")
        lines.append("|----------|-------|-------|------------|")
        
        for lang in languages[:5]:  # Top 5 languages
            lines.append(
                f"| {lang['language']} | {lang['files']} | "
                f"{lang['lines']:,} | {lang['percentage']:.1f}% |"
            )
        
        lines.append("")
    
    # Frameworks
    if tech_stack.get("frameworks"):
        lines.append("### Frameworks")
        for fw in tech_stack["frameworks"]:
            lines.append(f"- {fw}")
        lines.append("")
    
    # Databases
    if tech_stack.get("databases"):
        lines.append("### Databases")
        for db in tech_stack["databases"]:
            lines.append(f"- {db}")
        lines.append("")
    
    # Infrastructure
    if tech_stack.get("infrastructure"):
        lines.append("### Infrastructure & DevOps")
        for infra in tech_stack["infrastructure"]:
            lines.append(f"- {infra}")
        lines.append("")
    
    return "\n".join(lines)


def _format_architecture(report: Dict[str, Any]) -> str:
    """Format architecture insights section."""
    insights = report.get("key_insights", {})
    
    lines = [
        "## 🏗️ Architecture Insights",
        "",
    ]
    
    if insights.get("key_modules"):
        lines.extend([
            "### Key Modules",
            insights.get("key_modules"),
            "",
        ])
    
    if insights.get("tech_choices"):
        lines.extend([
            "### Technology Choices",
            insights.get("tech_choices"),
            "",
        ])
    
    return "\n".join(lines)


def _format_folder_structure(report: Dict[str, Any]) -> str:
    """Format folder structure section."""
    structure = report.get("structure", {})
    folders = structure.get("folders", [])
    
    lines = [
        "## 📁 Repository Structure",
        "",
        f"**Total Folders:** {structure.get('total_folders', 0)}",
        "",
    ]
    
    if folders:
        lines.append("| Folder | Role | Files |")
        lines.append("|--------|------|-------|")
        
        for folder in folders:
            role_emoji = {
                "backend": "⚙️",
                "frontend": "🎨",
                "api": "🔌",
                "database": "💾",
                "config": "⚙️",
                "tests": "🧪",
                "docs": "📚",
                "misc": "📦",
            }.get(folder["role"], "📦")
            
            lines.append(
                f"| `{folder['folder']}` | {role_emoji} {folder['role']} | "
                f"{folder['file_count']} |"
            )
        
        lines.append("")
    
    return "\n".join(lines)


def _format_entry_points(report: Dict[str, Any]) -> str:
    """Format entry points section."""
    entrypoints = report.get("entry_points", {})
    
    lines = [
        "## 🚀 Entry Points",
        "",
        f"**Total Entry Points:** {entrypoints.get('total_entrypoints', 0)}",
        "",
    ]
    
    # Application files
    app_files = entrypoints.get("application_files", [])
    if app_files:
        lines.append("### Application Files")
        for entry in app_files[:10]:  # Limit to 10
            lines.append(f"- `{entry['path']}` ({entry['type']})")
        lines.append("")
    
    # Framework entrypoints
    framework_entries = entrypoints.get("framework_entrypoints", [])
    if framework_entries:
        lines.append("### Framework Entry Points")
        for entry in framework_entries[:10]:
            lines.append(f"- `{entry['path']}` (Framework: {entry['framework']})")
        lines.append("")
    
    # Docker entrypoints
    docker_entries = entrypoints.get("docker_entrypoints", [])
    if docker_entries:
        lines.append("### Docker Entry Points")
        for entry in docker_entries[:5]:
            lines.append(f"- `{entry['path']}`")
            lines.append(f"  ```dockerfile")
            lines.append(f"  {entry['command']}")
            lines.append(f"  ```")
        lines.append("")
    
    return "\n".join(lines)


def _format_execution_flow(report: Dict[str, Any]) -> str:
    """Format execution flow section."""
    exec_flow = report.get("execution_flow", {})
    
    lines = [
        "## 🔄 Execution Flow",
        "",
    ]
    
    if exec_flow.get("entry_point"):
        lines.extend([
            "### Entry Point",
            exec_flow.get("entry_point"),
            "",
        ])
    
    if exec_flow.get("request_flow"):
        lines.extend([
            "### Request Flow",
            exec_flow.get("request_flow"),
            "",
        ])
    
    if exec_flow.get("key_interactions"):
        lines.extend([
            "### Key Interactions",
            exec_flow.get("key_interactions"),
            "",
        ])
    
    return "\n".join(lines)


def _format_module_summaries(report: Dict[str, Any]) -> str:
    """Format module summaries section."""
    structure = report.get("structure", {})
    folder_summaries = structure.get("folder_summaries", [])
    
    if not folder_summaries:
        return ""
    
    lines = [
        "## 📦 Module Summaries",
        "",
    ]
    
    for summary in folder_summaries[:10]:  # Limit to 10
        folder = summary.get("folder", "")
        role = summary.get("role", "")
        purpose = summary.get("purpose", "")
        
        lines.extend([
            f"### `{folder}` ({role})",
            "",
        ])
        
        if purpose:
            lines.extend([
                "**Purpose:**",
                purpose,
                "",
            ])
        
        if summary.get("key_components"):
            lines.extend([
                "**Key Components:**",
                summary.get("key_components"),
                "",
            ])
        
        if summary.get("interactions"):
            lines.extend([
                "**Interactions:**",
                summary.get("interactions"),
                "",
            ])
    
    return "\n".join(lines)


def _format_diagrams(report: Dict[str, Any]) -> str:
    """Format diagrams section."""
    diagrams = report.get("diagrams", {})
    
    lines = [
        "## 📊 Visual Diagrams",
        "",
    ]
    
    # Execution flow diagram
    if diagrams.get("flow_diagram"):
        lines.extend([
            "### Execution Flow Diagram",
            "",
            "```mermaid",
            diagrams.get("flow_diagram"),
            "```",
            "",
        ])
    
    # Module diagram
    if diagrams.get("module_diagram"):
        lines.extend([
            "### Module Structure Diagram",
            "",
            "```mermaid",
            diagrams.get("module_diagram"),
            "```",
            "",
        ])
    
    # Dependency diagram (optional, can be large)
    if diagrams.get("dependency_diagram"):
        lines.extend([
            "### Dependency Graph",
            "",
            "```mermaid",
            diagrams.get("dependency_diagram"),
            "```",
            "",
        ])
    
    return "\n".join(lines)


def _format_dependencies(report: Dict[str, Any]) -> str:
    """Format dependencies section (optional)."""
    dependencies = report.get("dependencies", {})
    
    lines = [
        "## 🔗 Dependencies",
        "",
        f"**Total Nodes:** {dependencies.get('total_nodes', 0)}  ",
        f"**Total Edges:** {dependencies.get('total_edges', 0)}  ",
        "",
    ]
    
    return "\n".join(lines)