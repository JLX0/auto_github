from __future__ import annotations

from charset_normalizer import detect

from auto_github.reimplementation.core import AutoReimplementation
from LLM_utils.inquiry import get_api_key
import os


def delete_file(file_path):
    # Check if the file exists and delete it
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' has been deleted successfully.")
        except Exception as e:
            print(f"An error occurred while trying to delete the file: {e}")
    else:
        print(f"File '{file_path}' not found.")

delete_file("/home/j/experiments/auto_github/examples/repos.json")
delete_file("/home/j/experiments/auto_github/sample_repos/bohb/main_code.py")

def dummy_test(code):
    print("performing dummy test")

def main() -> None:
    repo_link = "https://github.com/example_user/example_repo.git"  # Replace with your GitHub repo URL
    repo_path = '/home/j/experiments/auto_github/sample_repos/bohb'  # Replace with your local repo path

    key = get_api_key("../", "DeepSeek")
    auto_reimplementation_instance=AutoReimplementation(
        api_key=key,
        model="deepseek-chat",
        repo_link=repo_link,
        repo_path=repo_path,
        debug=True,
        external_tests=dummy_test
        )

    goal="""
    1. create a function called load_BOHB
    2. the arguments of the function should be: various hyperparameters for configuring BOHB
    3. the function should return an object, which is a callable that takes a fitness function as input and returns the best hyperparameters.   
    """
    auto_reimplementation_instance.run(goal=goal)

if __name__ == "__main__":
    main()

