"""
Repository loader for RepoAnalyzer.
Loads and structures GitHub repository data.
"""
import base64
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from github_client.client import GitHubClient
from github_client.filters import is_ignored_path, is_allowed_file, is_binary_file


class RepoLoader:
    """Loads and structures GitHub repository data."""
    
    def __init__(self):
        self.client = GitHubClient()
    
    @staticmethod
    def parse_repo_url(url: str) -> tuple[str, str]:
        """
        Extract owner and repo name from GitHub URL.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo)
            
        Raises:
            ValueError: If URL format is invalid
        """
        # Clean the URL
        url = url.strip().rstrip("/")
        
        # Extract the path after github.com
        if "github.com/" in url:
            # Split by github.com/ and take the part after it
            path = url.split("github.com/", 1)[1]
            
            # Remove .git suffix if present
            if path.endswith(".git"):
                path = path[:-4]
            
            # Split by / to get owner and repo
            parts = path.split("/")
            
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1]
                return owner, repo
        
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    def load_repository(self, repo_url: str, branch: Optional[str] = None) -> Dict[str, any]:
        """
        Load repository data and structure files.
        
        Args:
            repo_url: GitHub repository URL
            branch: Optional branch name (uses default branch if not specified)
            
        Returns:
            Dictionary containing repository metadata and file contents
        """
        # Parse repository URL
        owner, repo = self.parse_repo_url(repo_url)
        
        # Get repository metadata
        metadata = self.client.get_repo_metadata(owner, repo)
        
        # Use provided branch or default branch from metadata
        if not branch:
            branch = metadata.get("default_branch", "main")
        
        target_branch = branch
        print(f"DEBUG: Loading files from branch: {target_branch}")
        
        # Get repository tree
        tree_data = self.client.get_repo_tree(owner, repo, target_branch, recursive=True)
        
        # Load file contents
        files = self._load_files(owner, repo, tree_data.get("tree", []))
        
        return {
            "files": files,
            "metadata": {
                "owner": owner,
                "repo": repo,
                "branch": target_branch,
                "description": metadata.get("description", ""),
                "language": metadata.get("language", ""),
                "stars": metadata.get("stargazers_count", 0),
            }
        }
    
    def _load_files(self, owner: str, repo: str, tree: List[Dict]) -> List[Dict[str, str]]:
        """
        Load and filter file contents from repository tree.
        
        Args:
            owner: Repository owner
            repo: Repository name
            tree: Repository tree from GitHub API
            
        Returns:
            List of dictionaries with 'path' and 'content' keys
        """
        files = []  # Changed from dict to list
        
        for item in tree:
            # Only process blob (file) items
            if item.get("type") != "blob":
                continue
            
            path = item.get("path", "")
            
            # Apply filters
            if is_ignored_path(path) or not is_allowed_file(path):
                continue
            
            try:
                # Fetch file content
                content_data = self.client.get_file_content(owner, repo, path)
                
                # Decode Base64 content
                encoded_content = content_data.get("content", "")
                decoded_bytes = base64.b64decode(encoded_content)
                
                # Skip binary files
                if is_binary_file(decoded_bytes):
                    continue
                
                # Decode to UTF-8 text
                decoded_text = decoded_bytes.decode("utf-8", errors="ignore")
                
                # Append as dictionary with path and content
                files.append({
                    "path": path,
                    "content": decoded_text
                })
                
            except Exception as e:
                # Skip files that fail to load
                print(f"Warning: Failed to load {path}: {str(e)}")
                continue
        
        return files

