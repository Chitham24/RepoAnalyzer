"""
GitHub REST API wrapper for RepoAnalyzer.
Handles API requests with authentication and error handling.
"""
import time
from typing import Dict, Any, Optional
import requests
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE_URL, REQUEST_TIMEOUT


class GitHubClient:
    """Wrapper for GitHub REST API interactions."""
    
    def __init__(self):
        self.base_url = GITHUB_API_BASE_URL
        self.timeout = REQUEST_TIMEOUT
        self.session = requests.Session()
        
        # Attach authorization header if token exists
        if GITHUB_TOKEN:
            self.session.headers.update({
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            })
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        
        # Ensure base_url doesn't end with /
        base_url = self.base_url.rstrip("/")
        
        url = f"{base_url}{endpoint}"
        
        # Debug - remove after fixing
        print(f"DEBUG: Full URL = {url}")
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            # Handle rate limiting
            if response.status_code == 403 and "rate limit" in response.text.lower():
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                if reset_time:
                    wait_time = max(reset_time - int(time.time()), 0)
                    raise Exception(f"Rate limit exceeded. Resets in {wait_time} seconds.")
                raise Exception("Rate limit exceeded.")
            
            # Handle non-200 responses
            if response.status_code != 200:
                raise Exception(
                    f"GitHub API error: {response.status_code} - {response.text[:200]}"
                )
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_repo_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository metadata.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository metadata as JSON
        """
        endpoint = f"/repos/{owner}/{repo}"
        # DEBUG
        print(f"DEBUG: Requesting {self.base_url}/{endpoint}")
        # print(f"DEBUG: Token (last 4): ...{self.token[-4:]}")
        # DEBUG ENDS
        return self._make_request(endpoint)
    
    def get_repo_tree(self, owner: str, repo: str, branch: str = "main", recursive: bool = True) -> Dict[str, Any]:
        """
        Get repository tree.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name (will be resolved to SHA)
            recursive: Whether to get tree recursively
            
        Returns:
            Tree data
        """
        # Step 1: Get the branch to find the commit SHA
        branch_endpoint = f"/repos/{owner}/{repo}/branches/{branch}"
        print(f"DEBUG: Getting branch info from {branch_endpoint}")
        
        try:
            branch_data = self._make_request(branch_endpoint)
            commit_sha = branch_data["commit"]["sha"]
            print(f"DEBUG: Branch '{branch}' resolved to SHA: {commit_sha}")
        except Exception as e:
            # If branch not found, try 'master' as fallback
            if branch == "main":
                print(f"DEBUG: 'main' branch not found, trying 'master'")
                branch_endpoint = f"/repos/{owner}/{repo}/branches/master"
                branch_data = self._make_request(branch_endpoint)
                commit_sha = branch_data["commit"]["sha"]
            else:
                raise e
        
        # Step 2: Get the tree using the commit SHA
        tree_endpoint = f"/repos/{owner}/{repo}/git/trees/{commit_sha}"
        params = {"recursive": "1"} if recursive else {}
        
        print(f"DEBUG: Getting tree from {tree_endpoint}")
        return self._make_request(tree_endpoint, params)

    
    def get_file_content(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """
        Get file content from repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path in repository
            
        Returns:
            File content metadata as JSON (includes Base64 encoded content)
        """
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        return self._make_request(endpoint)
