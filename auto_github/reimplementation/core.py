from __future__ import annotations

from typing import Optional

from LLM_utils.inquiry import OpenAI_interface
from auto_github.reimplementation.repo_loader import Repo
from auto_github.reimplementation.prompt import ReimplementationPrompt

class AutoReimplementation:
    def __init__(
        self,
        api_key: str,
        model: str,
        repo_link: str,
        repo_path: str,
        debug: bool = False,
        mode: str = "default",
        approach: str = "load",
        storage_path: str = "repos.json",
    ) -> None:

        self.OpenAI_instance = OpenAI_interface(api_key , model=model , debug=debug)
        self.repo_link = repo_link
        self.repo_path = repo_path
        self.repo_instance = Repo(repo_link, repo_path, model=model)
        self.repo_instance.clone_repo()
        self.prompt_instance = ReimplementationPrompt()
        self.mode = mode
        self.approach = approach
        self.output: Optional[str] = None
        # self.storage_instance = Storage(storage_path)
        self.cost_accumulation = 0

    def run(self):
        # logic:
