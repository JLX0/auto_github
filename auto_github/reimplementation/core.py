from __future__ import annotations

from typing import Optional

from LLM_utils.inquiry import OpenAI_interface
from auto_github.reimplementation.repo_loader import Repo_ML
from auto_github.reimplementation.prompts import ReimplementationPromptML
from auto_github.utils.stored_info import Storage
from auto_github.reimplementation.sequence_tests import sequence_tests_LM
import traceback

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
        self.repo_instance = Repo_ML(repo_link, repo_path, storage_path, model=model)
        self.repo_instance.clone_repo()
        self.prompt_instance = ReimplementationPromptML()
        self.mode = mode
        self.approach = approach
        self.output: Optional[str] = None
        self.storage_instance = Storage(storage_path,repo_path)
        self.sequence_tests_LM_instance=sequence_tests_LM(repo_path,storage_path)
        self.cost_accumulation = 0
        self.sequence_tests_trial_limit=5

        self.trials={"environment_designation":0,"main_designation":0}

    def run(self,goal=None):
        if self.mode == "default" :
            self.load_basic_information()
            self.designate_files_environments()
            self.designate_files_main(goal)
            self.generate_code_environments()

    def send_inquiry(self,tests=None):
        if tests:
            response, cost = self.OpenAI_instance.ask_with_test(self.prompt_instance.prompt , tests)
        else:
            response, cost = self.OpenAI_instance.ask(self.prompt_instance.prompt)
        self.cost_accumulation += cost
        return response


    @staticmethod
    def auto_load_save(method) :
        """
        Decorator to automatically call self.load_info() before the method
        and self.save_info() after the method.
        """

        def wrapper(self , *args , **kwargs) :
            self.storage_instance.load_info()
            result = method(self , *args , **kwargs)
            self.storage_instance.save_info()
            return result

        return wrapper  # Return the wrapper function

    def load_basic_information(self):
        self.repo_instance.generate_and_get_repo_structure()
        self.repo_instance.load_file_contents(mode="main")
        self.repo_instance.load_file_contents(mode="environment")
        self.repo_instance.load_file_contents(targets=['README.md'])

    @auto_load_save
    def designate_files_environments(self):
        readme=self.storage_instance.information[self.repo_path]['file_contents']['repo_root/README.md']
        file_structure=self.storage_instance.information[self.repo_path]['file_structure']
        self.prompt_instance.designate_files_environments(file_structure,readme)
        extraction=self.send_inquiry(tests=self.sequence_tests_LM_instance.designate_files_tests)
        self.trials["environment_designation"] +=1
        self.storage_instance.add_designated_entries("environments",extraction,self.trials["environment_designation"])

    def generate_code_environments(self):
        file_contents = self.storage_instance.information[self.repo_path]['file_contents']
        readme = file_contents['repo_root/README.md']
        file_structure = self.storage_instance.information[self.repo_path]['file_structure']
        trial_environment_designation="1"
        file_list = self.storage_instance.information[self.repo_path]['environments'][trial_environment_designation]
        environment_name = "test_1"
        self.prompt_instance.generate_code_environments(environment_name,readme,file_structure,file_list,file_contents)
        extraction = self.send_inquiry(self.sequence_tests_LM_instance.generate_code_environments_tests)
        print(extraction)

    @auto_load_save
    def designate_files_main(self , goal):
        readme=self.storage_instance.information[self.repo_path]['file_contents']['repo_root/README.md']
        file_structure=self.storage_instance.information[self.repo_path]['file_structure']
        self.prompt_instance.designate_files_main(goal,file_structure,readme)
        extraction=self.send_inquiry(tests=self.sequence_tests_LM_instance.designate_files_tests)
        self.trials["main_designation"] +=1
        self.storage_instance.add_designated_entries("main",extraction,self.trials["main_designation"])

