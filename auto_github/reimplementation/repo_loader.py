import os
import subprocess
from pathlib import Path

from auto_github.utils.stored_info import Storage



class Repo_base:
    def __init__(self, repo_link: str, repo_path: str, storage_path:str, model: str = "gpt-4o-mini") -> None:
        """Initialize the Repository instance with the given path and model."""
        self.repo_link: str = repo_link
        self.repo_path: str = repo_path
        self.file_structure: str = ""
        self.file_contents: dict[str, str] = {}
        self.model: str = model
        self.storage_instance = Storage(storage_path, repo_path)

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

    def generate_and_get_repo_structure_base(self , indent: str = '') -> str:
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
                markdown += self.generate_and_get_repo_structure_base(indent + '  ')
                # Restore the original repo_path
                self.repo_path = original_repo_path
            else:
                markdown += f"{indent}- {item}\n"

        # Store the generated structure in the instance variable
        if indent == '':  # Only store the structure for the top-level directory
            self.file_structure = markdown


        return markdown

    def generate_and_get_repo_structure(self , indent: str = '') -> str :
        # Generate the markdown structure
        markdown = self.generate_and_get_repo_structure_base(indent)

        # Prepend 'repo_root' and indent the entire structure under it
        markdown_with_root = f"- **repo_root/**\n"
        for line in markdown.splitlines() :
            markdown_with_root += f"  {line}\n"  # Indent each line under repo_root

        # Store the generated structure in the instance variable
        self.file_structure = markdown_with_root

        # Add the file structure to storage
        self.storage_instance.add_file_structure(self.file_structure)

        return markdown_with_root


class Repo_ML(Repo_base):

    def __init__(self, repo_link: str, repo_path: str, storage_path:str, model: str = "gpt-4o-mini") -> None:
        super().__init__(repo_link,repo_path,storage_path, model)
        self.supported_main_file_types: list[str] = ['.py' , '.json']
        self.supported_environment_file_types: list[str] = ['.yml' , '.yaml']
        self.supported_data_file_types: list[str] = ['.csv' , '.tsv' , '.json']
        # TODO: complete the file files


    def load_file_contents(self, targets: list[str] = None, mode="main") -> dict[str, str]:
        """
        Load the contents of files in the repository into a dictionary.

        Args:
            targets (list[str], optional): List of file paths to load. If None, loads all files of main types.
            mode (str, optional): Mode to determine which files to load. Defaults to "main".

        Returns:
            dict[str, str]: Dictionary with file paths as keys (with "repo_root" replacing the actual repo path)
                           and file contents as values.
        """

        if targets is None:
            if mode == "main":
            # Load all files with extensions in self.main_file_types
                target_files=self.supported_main_file_types
            if mode == "environment":
                target_files=self.supported_environment_file_types
            for root, _, files in os.walk(self.repo_path):
                for file in files:
                    if any(file.endswith(ext) for ext in target_files):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                # Replace self.repo_path with "repo_root" in the file path
                                relative_path = os.path.relpath(file_path, self.repo_path)
                                repo_root_path = os.path.join("repo_root", relative_path)
                                self.file_contents[repo_root_path] = f.read()
                        except Exception as e:
                            print(f"Failed to read file {file_path}: {e}")

        elif targets and isinstance(targets, list):
            # Load only the specified files
            for target in targets:
                file_path = os.path.join(self.repo_path, target)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            # Replace self.repo_path with "repo_root" in the file path
                            relative_path = os.path.relpath(file_path, self.repo_path)
                            repo_root_path = os.path.join("repo_root", relative_path)
                            self.file_contents[repo_root_path] = f.read()
                    except Exception as e:
                        print(f"Failed to read file {file_path}: {e}")
                else:
                    print(f"File {file_path} does not exist.")

        self.storage_instance.add_file_contents(self.file_contents)

        return self.file_contents



if __name__ == "__main__":
    # Example usage
    repo_link = "https://github.com/example_user/example_repo.git"  # Replace with your GitHub repo URL
    repo_path = '/home/j/experiments/auto_github/sample_repos/bohb'  # Replace with your local repo path
    repo = Repo_ML(repo_link, repo_path, storage_path="info.json")
    repo.clone_repo()  # Clone the repository
    markdown_structure = repo.generate_and_get_repo_structure_base()  # Generate and print the structure
    print(markdown_structure)

    file_contents = repo.load_file_contents(mode="environment")
    print(file_contents)
    # # Load all main file types
    # file_contents = repo.load_file_contents()
    # print(file_contents)
    #
    # # Load specific files
    # specific_files = ['README.md', 'src/main.py']
    # file_contents = repo.load_file_contents(targets=specific_files)
    # print(file_contents)