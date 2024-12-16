import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

def search_github_repositories(query, token, max_results=100):
    """
    Search GitHub repositories by query, sorted by last update (newest first).

    :param query: The search query string (e.g., "American Sign Language" or "ASL").
    :param token: GitHub personal access token for authentication.
    :param max_results: Maximum number of results to retrieve.
    :return: List of repositories matching the query.
    """
    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"token {token}"}
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": 50  # GitHub limits to 50 per page
    }

    results = []
    try:
        print(f"Accessing GitHub for query: {query}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        results.extend(data.get("items", []))

        # If more results are requested than the API allows in one page, handle pagination
        while "next" in response.links and len(results) < max_results:
            response = requests.get(response.links["next"]["url"], headers=headers)
            response.raise_for_status()
            data = response.json()
            results.extend(data.get("items", []))

        return results[:max_results]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repositories: {e}")
        return []

def save_repositories_to_file(repositories, file_path):
    """
    Save the list of repositories to a text file.

    :param repositories: List of repository objects.
    :param file_path: Path to the output file.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            if not repositories:
                file.write("No repositories found.\n")
                return

            file.write(f"Found {len(repositories)} repositories:\n\n")
            for repo in repositories:
                file.write(f"Name: {repo['name']}\n")
                file.write(f"Description: {repo.get('description', 'No description')}\n")
                file.write(f"Stars: {repo['stargazers_count']}\n")
                file.write(f"Last Updated: {repo['updated_at']}\n")
                file.write(f"URL: {repo['html_url']}\n\n")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    # Load the GitHub token from .env
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GitHub token not found. Please add it to a .env file.")
        exit(1)

    # Define the search queries
    queries = ["American Sign Language", "ASL"]
    output_file = "C:\\Users\\toddk\\Documents\\asl_github_repositories.txt"

    # Search for repositories and combine results
    all_repositories = []
    for query in queries:
        all_repositories.extend(search_github_repositories(query, token))

    # Remove duplicate repositories by URL
    unique_repositories = {repo['html_url']: repo for repo in all_repositories}.values()

    # Save the results to a file
    save_repositories_to_file(list(unique_repositories), output_file)
    print(f"Repositories saved to {output_file}")
