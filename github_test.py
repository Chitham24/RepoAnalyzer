from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.github.com/repos/octocat/Hello-World", headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
