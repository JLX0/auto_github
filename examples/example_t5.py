from __future__ import annotations

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

delete_file("/examples/repos_t5_worked.json")
delete_file("/home/j/experiments/auto_github/sample_repos/bohb/main_code.py")

def main() -> None:
    repo_link = "https://github.com/google-research/text-to-text-transfer-transformer.git"  # Replace with your GitHub repo URL
    repo_path = '/home/j/experiments/auto_github/sample_repos/t5'  # Replace with your local repo path

    key = get_api_key("../", "DeepSeek")
    auto_reimplementation_instance=AutoReimplementation(
        api_key=key,
        model="deepseek-chat",
        repo_link=repo_link,
        repo_path=repo_path,
        debug=True,
        external_tests_path="sample_test_t5.py",
        target_path="/home/j/experiments/auto_github/sample_repos/",
        target_name="main_code.py"
        )

    goal="""
    1. create a function called load_T5
    2. the arguments of the function should be: various hyperparameters for configuring T5
    3. the function should return an object, which is a torch.nn.Module that takes a batch of input sequences and returns the output sequences.
    """
    auto_reimplementation_instance.run(goal=goal)

if __name__ == "__main__":
    main()

