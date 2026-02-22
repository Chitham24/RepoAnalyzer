"""
Repository-level summarizer for RepoAnalyzer.
Generates comprehensive repository overview combining all analysis results.
"""
from typing import Dict, List
from llm.client import LLMClient
from llm.prompts import repo_architecture_prompt, execution_flow_prompt


class RepoSummarizer:
    """Generates comprehensive repository-level summaries."""
    
    def __init__(self):
        self.client = LLMClient()
    
    def summarize_architecture(
        self,
        repo_name: str,
        description: str,
        languages: Dict[str, any],
        frameworks: List[str],
        databases: List[str],
        infrastructure: List[str],
        folder_summaries: List[Dict[str, str]],
        entrypoints: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, str]:
        """
        Generate comprehensive architecture summary for the repository.
        
        Args:
            repo_name: Repository name
            description: Repository description
            languages: Language statistics from analysis
            frameworks: Detected frameworks
            databases: Detected databases
            infrastructure: Detected infrastructure tools
            folder_summaries: List of folder summaries
            entrypoints: Detected entry points
            
        Returns:
            Dictionary with architecture summary containing:
            - repo_name: Repository name
            - summary: Full architecture summary
            - purpose: Project purpose
            - architecture: Architecture description
            - key_modules: Key modules description
            - tech_choices: Technology choices rationale
        """
        try:
            # Generate prompt
            prompt = repo_architecture_prompt(
                repo_name=repo_name,
                description=description,
                languages=languages,
                frameworks=frameworks,
                databases=databases,
                infrastructure=infrastructure,
                folder_summaries=folder_summaries,
                entrypoints=entrypoints
            )
            
            # Get summary from LLM
            summary = self.client.generate(prompt)
            
            # Parse structured information
            purpose = self._extract_section(summary, "Project Purpose")
            architecture = self._extract_section(summary, "Architecture")
            key_modules = self._extract_section(summary, "Key Modules")
            tech_choices = self._extract_section(summary, "Technology Choices")
            
            return {
                "repo_name": repo_name,
                "summary": summary,
                "purpose": purpose,
                "architecture": architecture,
                "key_modules": key_modules,
                "tech_choices": tech_choices,
            }
            
        except Exception as e:
            return {
                "repo_name": repo_name,
                "summary": f"Error generating architecture summary: {str(e)}",
                "purpose": None,
                "architecture": None,
                "key_modules": None,
                "tech_choices": None,
            }
    
    def summarize_execution_flow(
        self,
        repo_name: str,
        entrypoints: Dict[str, List[Dict[str, str]]],
        frameworks: List[str],
        folder_summaries: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Generate execution flow summary for the repository.
        
        Args:
            repo_name: Repository name
            entrypoints: Detected entry points
            frameworks: Detected frameworks
            folder_summaries: List of folder summaries
            
        Returns:
            Dictionary with execution flow summary containing:
            - repo_name: Repository name
            - summary: Full execution flow summary
            - entry_point: Entry point description
            - request_flow: Request flow description
            - key_interactions: Key interactions description
        """
        try:
            # Generate prompt
            prompt = execution_flow_prompt(
                repo_name=repo_name,
                entrypoints=entrypoints,
                frameworks=frameworks,
                folder_summaries=folder_summaries
            )
            
            # Get summary from LLM
            summary = self.client.generate(prompt)
            
            # Parse structured information
            entry_point = self._extract_section(summary, "Entry Point")
            request_flow = self._extract_section(summary, "Request Flow")
            key_interactions = self._extract_section(summary, "Key Interactions")
            
            return {
                "repo_name": repo_name,
                "summary": summary,
                "entry_point": entry_point,
                "request_flow": request_flow,
                "key_interactions": key_interactions,
            }
            
        except Exception as e:
            return {
                "repo_name": repo_name,
                "summary": f"Error generating execution flow summary: {str(e)}",
                "entry_point": None,
                "request_flow": None,
                "key_interactions": None,
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """
        Extract a specific section from the summary.
        
        Args:
            text: Full summary text
            section_name: Name of section to extract
            
        Returns:
            Extracted section text or None
        """
        lines = text.split("\n")
        in_section = False
        section_lines = []
        
        for line in lines:
            # Check if this line starts the section
            if section_name.lower() in line.lower() and (":" in line or "#" in line):
                in_section = True
                # If there's content after the colon on the same line, include it
                if ":" in line:
                    after_colon = line.split(":", 1)[1].strip()
                    if after_colon:
                        section_lines.append(after_colon)
                continue
            
            # Check if we've reached a new section
            if in_section and line.strip() and (line.strip().endswith(":") or line.startswith("#")):
                break
            
            # Add line to section if we're in it
            if in_section and line.strip():
                section_lines.append(line.strip())
        
        return "\n".join(section_lines) if section_lines else None
