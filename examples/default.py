from __future__ import annotations

from auto_github.reimplementation.core import AutoReimplementation
from LLM_utils.inquiry import get_api_key

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
        )

    goal="""
    1. create a function called load_BOHB
    2. the arguments of the function should be: various hyperparameters for configuring BOHB
    3. the function should return an object, which is a callable that takes a fitness function as input and returns the best hyperparameters.   
    """
    auto_reimplementation_instance.run(goal=goal)

if __name__ == "__main__":
    main()

