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
    auto_reimplementation_instance.run()

if __name__ == "__main__":
    main()

