from __future__ import annotations

from typing import Optional

from LLM_utils.inquiry import OpenAI_interface
from auto_github.reimplementation.repo_loader import Repo_ML
from auto_github.reimplementation.prompt import ReimplementationPromptML

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
        self.repo_instance = Repo_ML(repo_link, repo_path, model=model)
        self.repo_instance.clone_repo()
        self.prompt_instance = ReimplementationPromptML()
        self.mode = mode
        self.approach = approach
        self.output: Optional[str] = None
        # self.storage_instance = Storage(storage_path)
        self.cost_accumulation = 0
    def run(self):
        if self.mode == "default" :
            self.load_basic_information()
            self.designate_file_environments()

    def send_inquiry(self,tests=None):
        if tests:
            response, cost = self.OpenAI_instance.ask_with_test(self.prompt_instance.prompt , tests)
        else:
            response, cost = self.OpenAI_instance.ask(self.prompt_instance.prompt)
        self.cost_accumulation += cost
        return response

    def load_basic_information(self):
        self.repo_instance.generate_and_get_repo_structure()
        self.repo_instance.load_file_contents()
        self.repo_instance.load_file_contents(targets=['README.md'])

    def designate_file_environments(self):
        readme=self.repo_instance.file_contents['repo_root/README.md']
        self.prompt_instance.designate_files_environments(self.repo_instance.file_structure,readme)
        response = self.send_inquiry()
        print(response)




