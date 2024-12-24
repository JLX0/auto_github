import requests

def search_github_repos(keyword, max_results=10):
    """
    Search GitHub repositories using a keyword.

    Args:
        keyword (str): The keyword to search for.
        max_results (int): Maximum number of repositories to return.

    Returns:
        list: A list of repositories with basic details.
    """
    base_url = "https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github+json"}
    params = {
        "q": keyword,
        "sort": "stars",
        "order": "desc",
        "per_page": max_results
    }

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        repositories = []

        for repo in data.get("items", []):
            repositories.append({
                "name": repo["name"],
                "url": repo["html_url"],
                "description": repo.get("description"),
                "stars": repo["stargazers_count"]
            })
        return repositories
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

if __name__ == "__main__":
    keyword = input("Enter a keyword to search for GitHub repositories: ")
    max_results = int(input("Enter the maximum number of results to display: "))

    repos = search_github_repos(keyword, max_results)

    if repos:
        print("\nTop Repositories:")
        for idx, repo in enumerate(repos, start=1):
            print(f"{idx}. {repo['name']} ({repo['stars']} stars)")
            print(f"   URL: {repo['url']}")
            print(f"   Description: {repo['description']}\n")
    else:
        print("No repositories found.")
