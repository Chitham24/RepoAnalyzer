"""
File-level summarizer for RepoAnalyzer.
Generates summaries for individual code files using LLM.
"""
from typing import Dict
from llm.client import LLMClient
from llm.prompts import file_summary_prompt
from analysis.language_detector import detect_language


class FileSummarizer:
    """Generates summaries for individual files."""
    
    def __init__(self):
        self.client = LLMClient()
    
    def summarize_file(self, file_path: str, content: str) -> Dict[str, str]:
        """
        Summarize a single file.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Dictionary with structured summary containing:
            - path: File path
            - language: Detected language
            - summary: LLM-generated summary
            - purpose: Extracted purpose
            - responsibilities: Key responsibilities
            - dependencies: Key dependencies
        """
        # Detect language
        language = detect_language(file_path)
        
        # Skip if content is too short or language unknown
        if len(content.strip()) < 10 or language == "Unknown":
            return {
                "path": file_path,
                "language": language,
                "summary": "File skipped: insufficient content or unknown language",
                "purpose": None,
                "responsibilities": None,
                "dependencies": None,
            }
        
        try:
            # Generate prompt
            prompt = file_summary_prompt(file_path, language, content)
            
            # Get summary from LLM
            summary = self.client.generate(prompt)
            
            # Parse structured information (basic extraction)
            purpose = self._extract_section(summary, "Purpose")
            responsibilities = self._extract_section(summary, "Responsibilities")
            dependencies = self._extract_section(summary, "Key Dependencies")
            
            return {
                "path": file_path,
                "language": language,
                "summary": summary,
                "purpose": purpose,
                "responsibilities": responsibilities,
                "dependencies": dependencies,
            }
            
        except Exception as e:
            return {
                "path": file_path,
                "language": language,
                "summary": f"Error generating summary: {str(e)}",
                "purpose": None,
                "responsibilities": None,
                "dependencies": None,
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