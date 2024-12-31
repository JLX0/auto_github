import subprocess

def clone_repo(github_url , target_dir=None) :
    """
    Clones a GitHub repository to the specified directory.

    :param github_url: The URL of the GitHub repository.
    :param target_dir: The target directory to clone the repository into. If None, uses the repository name.
    """
    try :
        if target_dir :
            command = ['git' , 'clone' , github_url , target_dir]
        else :
            command = ['git' , 'clone' , github_url]

        # Run the git clone command
        subprocess.run(command , check=True)
        print(f"Repository cloned successfully.")
    except subprocess.CalledProcessError as e :
        print(f"Failed to clone repository: {e}")


# Example usage
github_link = "https://github.com/automl/HpBandSter"
target_dir = "/home/j/experiments/auto_github/sample_repos/bohb"
clone_repo(github_link , target_dir)
