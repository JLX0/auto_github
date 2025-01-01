import requests
import base64


def get_readme_content(repo_url) :
    # Extract owner and repo from the URL
    try :
        parts = repo_url.rstrip('/').split('/')
        owner , repo = parts[-2] , parts[-1]
    except IndexError :
        raise ValueError("Invalid GitHub repository URL.")

    # API endpoint to fetch README
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    # Send a GET request to the API
    response = requests.get(api_url)
    if response.status_code == 200 :
        data = response.json()
        readme_content = base64.b64decode(data['content']).decode('utf-8')
        return readme_content
    elif response.status_code == 404 :
        raise FileNotFoundError("README.md not found or repository does not exist.")
    else :
        raise Exception(f"Error fetching README: {response.status_code} {response.reason}")

if __name__ == "__main__":
    # Example usage:
    repo_url = "https://github.com/mlabonne/llm-course"
    try :
        readme = get_readme_content(repo_url)
        print(readme)
    except Exception as e :
        print(f"Error: {e}")