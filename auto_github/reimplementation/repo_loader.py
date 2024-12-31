import os
import subprocess
from pathlib import Path

class Repo:
    def __init__(self, repo_link: str, repo_path: str, model: str = "gpt-4o-mini") -> None:
        """Initialize the Repository instance with the given path and model."""
        self.repo_link: str = repo_link
        self.repo_path: str = repo_path
        self.file_structure: str = ""
        self.file_contents: dict[str, str] = {}
        self.model: str = model

    def clone_repo(self) -> None :
        """
        Clones the GitHub repository to the specified directory using instance variables.
        Skips cloning if the repository is already cloned in self.repo_path.
        """
        # Check if the repository is already cloned
        if os.path.exists(self.repo_path) and os.path.isdir(
                os.path.join(self.repo_path , '.git')) :
            print(f"Repository already exists in {self.repo_path}. Skipping cloning.")
            return

        try :
            # Use self.repo_link and self.repo_path
            command = ['git' , 'clone' , self.repo_link , self.repo_path]
            # Run the git clone command
            subprocess.run(command , check=True)
            print(f"Repository cloned successfully into {self.repo_path}.")
        except subprocess.CalledProcessError as e :
            print(f"Failed to clone repository: {e}")

    def generate_and_get_repo_structure(self, indent: str = '') -> str:
        """
        Recursively generate a markdown representation of the directory structure,
        store it in self.file_structure, and return it.
        """
        # Validate the directory
        repo_path = Path(self.repo_path)
        if not repo_path.is_dir():
            raise ValueError("The provided path is not a directory.")

        markdown = ''
        for item in sorted(os.listdir(self.repo_path)):
            full_path = os.path.join(self.repo_path, item)
            if os.path.isdir(full_path):
                markdown += f"{indent}- **{item}/**\n"
                # Temporarily update self.repo_path to the subdirectory for recursion
                original_repo_path = self.repo_path
                self.repo_path = full_path
                markdown += self.generate_and_get_repo_structure(indent + '  ')
                # Restore the original repo_path
                self.repo_path = original_repo_path
            else:
                markdown += f"{indent}- {item}\n"

        # Store the generated structure in the instance variable
        if indent == '':  # Only store the structure for the top-level directory
            self.file_structure = markdown

        return markdown


if __name__ == "__main__":
    # Example usage
    repo_link = "https://github.com/example_user/example_repo.git"  # Replace with your GitHub repo URL
    repo_path = '/home/j/experiments/auto_github/sample_repos/bohb'  # Replace with your local repo path
    repo = Repo(repo_link, repo_path)
    repo.clone_repo()  # Clone the repository
    markdown_structure = repo.generate_and_get_repo_structure()  # Generate and print the structure
    print(markdown_structure)