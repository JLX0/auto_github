import os
from pathlib import Path

def generate_markdown_structure(directory, indent=''):
    markdown = ''
    for item in sorted(os.listdir(directory)):
        full_path = os.path.join(directory, item)
        if os.path.isdir(full_path):
            markdown += f"{indent}- **{item}/**\n"
            markdown += generate_markdown_structure(full_path, indent + '  ')
        else:
            markdown += f"{indent}- {item}\n"
    return markdown

def get_repo_structure(repo_path):
    repo_path = Path(repo_path)
    if not repo_path.is_dir():
        raise ValueError("The provided path is not a directory.")

    markdown_structure = generate_markdown_structure(repo_path)
    return markdown_structure

# Example usage
repo_path = '/home/j/experiments/auto_github/sample_repos/bohb'  # Replace with your local repo path
markdown_structure = get_repo_structure(repo_path)
print(markdown_structure)