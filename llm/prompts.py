"""
Centralized prompt templates for RepoAnalyzer.
Provides deterministic prompts for code analysis tasks.
"""
from typing import Dict, List


def file_summary_prompt(file_path: str, language: str, content: str) -> str:
    """
    Generate prompt for file-level code summary.
    
    Args:
        file_path: Path to the file
        language: Programming language
        content: File content
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
        Analyze the following {language} file.

        File: {file_path}

        Rules:
        - No introduction or conclusion
        - Be strictly factual
        - Use bullet points only
        - Each bullet ≤ 20 words

        Output format EXACTLY:

        Purpose:
        - <single bullet>

        Responsibilities:
        - <max 3 bullets>

        Key Dependencies:
        - <max 3 bullets>

        Code:
        {content}
        """.strip()
    
    return prompt


def folder_summary_prompt(folder_path: str, file_summaries: List[Dict[str, str]]) -> str:
    """
    Generate prompt for folder/module-level summary.
    
    Args:
        folder_path: Path to the folder
        file_summaries: List of file summaries in the folder
        
    Returns:
        Formatted prompt string
    """
    summaries_text = "\n\n".join([
        f"File: {s['path']}\n{s['summary']}"
        for s in file_summaries
    ])
    
    prompt = f"""
        Summarize the module below.

        Folder: {folder_path}

        Rules:
        - No filler text
        - Bullet points only
        - Max bullets strictly enforced
        - Each bullet ≤ 20 words

        Output format EXACTLY:

        Module Purpose:
        - <max 2 bullets>

        Key Components:
        - <max 5 bullets>

        Interactions:
        - <max 2 bullets>

        File Summaries:
        {summaries_text}
        """.strip()
    
    return prompt


def repo_architecture_prompt(
    repo_name: str,
    description: str,
    languages: Dict[str, any],
    frameworks: List[str],
    databases: List[str],
    infrastructure: List[str],
    folder_summaries: List[Dict[str, str]],
    entrypoints: Dict[str, List[Dict[str, str]]]
) -> str:
    """
    Generate prompt for repository-level architecture summary.
    
    Args:
        repo_name: Repository name
        description: Repository description
        languages: Language statistics
        frameworks: Detected frameworks
        databases: Detected databases
        infrastructure: Detected infrastructure tools
        folder_summaries: Summaries of all folders
        entrypoints: Detected entry points
        
    Returns:
        Formatted prompt string
    """
    # Format languages
    lang_text = ", ".join([f"{lang} ({info['percentage']}%)" 
                           for lang, info in list(languages.items())[:5]])
    
    # Format tech stack
    frameworks_text = ", ".join(frameworks) if frameworks else "None detected"
    databases_text = ", ".join(databases) if databases else "None detected"
    infra_text = ", ".join(infrastructure) if infrastructure else "None detected"
    
    # Format folder summaries
    folders_text = "\n\n".join([
        f"Folder: {s['folder']}\nRole: {s['role']}\n{s['summary']}"
        for s in folder_summaries
    ])
    
    # Format entrypoints
    entry_files = [e['path'] for e in entrypoints.get('application_files', [])]
    entry_text = ", ".join(entry_files[:5]) if entry_files else "None detected"
    
    prompt = f"""
        Analyze the repository architecture.

        Repository: {repo_name}
        Description: {description}

        Languages: {lang_text}
        Frameworks: {", ".join(frameworks) if frameworks else "None"}
        Databases: {", ".join(databases) if databases else "None"}
        Infrastructure: {", ".join(infrastructure) if infrastructure else "None"}
        Entry Points: {", ".join(entry_files) if entry_files else "None"}

        Rules:
        - No introduction or summary paragraph
        - Bullet points only
        - Each bullet ≤ 16 words

        Output format EXACTLY:

        Project Purpose:
        - <max 2 bullets>

        Architecture:
        - <max 3 bullets>

        Key Modules:
        - <max 6 bullets>

        Technology Choices:
        - <max 3 bullets>

        Module Details:
        {folders_text}
        """.strip()
            
    return prompt


def execution_flow_prompt(
    repo_name: str,
    entrypoints: Dict[str, List[Dict[str, str]]],
    frameworks: List[str],
    folder_summaries: List[Dict[str, str]]
) -> str:
    """
    Generate prompt for high-level execution flow extraction.
    
    Args:
        repo_name: Repository name
        entrypoints: Detected entry points
        frameworks: Detected frameworks
        folder_summaries: Summaries of all folders
        
    Returns:
        Formatted prompt string
    """
    # Format entrypoints
    app_entries = "\n".join(
        f"- {e['path']} ({e['type']})"
        for e in entrypoints.get("application_files", [])[:5]
    )

    backend_folders = "\n".join(
        f"{s['folder']}:\n{s['summary']}"
        for s in folder_summaries if s["role"] in ["backend", "api"]
    )

    return f"""
        Describe the execution flow.

        Repository: {repo_name}
        Frameworks: {", ".join(frameworks) if frameworks else "None"}

        Rules:
        - No paragraphs
        - Numbered steps only
        - Max 6 steps
        - Each step ≤ 16 words

        Output format EXACTLY:

        Entry Point:
        - <1 bullet>

        Request Flow:
        1. <step>
        2. <step>
        3. <step>

        Key Interactions:
        - <max 4 bullets>

        Entry Files:
        {app_entries}

        Relevant Modules:
        {backend_folders}
        """.strip()
    
    return prompt
