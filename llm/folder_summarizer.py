"""
Folder-level summarizer for RepoAnalyzer.
Generates summaries for folders/modules using file summaries.
"""
from typing import Dict, List
from llm.client import LLMClient
from llm.prompts import folder_summary_prompt


class FolderSummarizer:
    """Generates summaries for folders/modules."""
    
    def __init__(self):
        self.client = LLMClient()
    
    def summarize_folder(
        self,
        folder_path: str,
        folder_role: str,
        file_summaries: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Summarize a folder/module based on its file summaries.
        
        Args:
            folder_path: Path to the folder
            folder_role: Role of folder (from structure analyzer)
            file_summaries: List of file summary dicts from FileSummarizer
            
        Returns:
            Dictionary with structured summary containing:
            - folder: Folder path
            - role: Folder role
            - summary: LLM-generated summary
            - purpose: Module purpose
            - key_components: Main components
            - interactions: Interaction patterns
        """
        # Filter out files with errors or skipped
        valid_summaries = [
            s for s in file_summaries
            if s.get("summary") and not s["summary"].startswith("Error") and not s["summary"].startswith("File skipped")
        ]
        
        # If no valid summaries, return basic info
        if not valid_summaries:
            return {
                "folder": folder_path,
                "role": folder_role,
                "summary": f"Folder contains {len(file_summaries)} files but no detailed summaries available.",
                "purpose": None,
                "key_components": None,
                "interactions": None,
            }
        
        # Limit to top files to avoid token limits
        summaries_to_use = valid_summaries[:10]
        
        try:
            # Generate prompt
            prompt = folder_summary_prompt(folder_path, summaries_to_use)
            
            # Get summary from LLM
            summary = self.client.generate(prompt)
            
            # Parse structured information
            purpose = self._extract_section(summary, "Module Purpose")
            key_components = self._extract_section(summary, "Key Components")
            interactions = self._extract_section(summary, "Interactions")
            
            return {
                "folder": folder_path,
                "role": folder_role,
                "summary": summary,
                "purpose": purpose,
                "key_components": key_components,
                "interactions": interactions,
            }
            
        except Exception as e:
            return {
                "folder": folder_path,
                "role": folder_role,
                "summary": f"Error generating folder summary: {str(e)}",
                "purpose": None,
                "key_components": None,
                "interactions": None,
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