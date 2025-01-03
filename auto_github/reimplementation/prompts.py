from __future__ import annotations

from typing import Optional

from LLM_utils.prompter import PromptBase

class ReimplementationPromptML(PromptBase):

    def __init__(self) -> None:
        self.environment_template_path="/home/j/experiments/auto_github/auto_github/reimplementation/environment_template.sh"

    def designate_files(self,
                        repository_structure: str,
                        goal: str,
                        repository_information: str,
                        response_header: str,
                        ):
        prompt_string = [
            "Given a file structure of a Github repository, a programming goal, and some "
            "information about the repository, your task is to designate the files that are "
            "important to reference to achieve the goal.",
            "Here is the file structure of the repository:",
            repository_structure,
            "Here is the programming goal:",
            goal,
            "Here is some information about the repository:",
            repository_information,
            "Your answer should be a Python list of strings. Your answer should not include any introduction, explanation, or context.",
            "Here is the Python list of string, with each string representing an the file path (starting with 'repo_root/') and file name of an important file for "+response_header,
        ]
        self.prompt = self.prompt_formatting_OpenAI(prompt_string)

    def designate_files_environments(self,repository_structure,repository_information):
        goal=("Configure and set up external environments required for the project’s core functionality,"
              " excluding documentation, GUI, and any modules or packages with source code already available in the repository.")
        repository_information=f"The content in the README.md file is as below:\n{repository_information}"
        response_header="configuring and setting up external environments:"
        self.designate_files(repository_structure,goal,repository_information,response_header)

    def designate_files_main(self,goal,repository_structure,repository_information):
        goal+=goal+"\n"+"Here are some additional context\n1. you should ignore files for documentation or GUI\n2. you should assume the external environments are already set up.\n3. the modules and packages in the repository are available and accessible (by importing for example)"
        repository_information=f"The content in the README.md file is as below:\n{repository_information}"
        response_header="achieving the goal:"
        self.designate_files(repository_structure,goal,repository_information,response_header)

    def file_contents_to_prompts(self , file_list: list[str] , file_contents:dict[str,str]):
        file_contents_string=[]
        for file in file_list:
            file_contents_string+=([f"-----File path and file name:{file}-----"])
            file_contents_string+=([f"File content:\n{file_contents[file]}"])
        return file_contents_string

    def load_environment_template(self):
        with open(self.environment_template_path, "r") as file:
            environment_template = file.read()
        return environment_template

    def generate_code_environments(self,environment_name,repository_information, repository_structure,file_list, file_contents):
        file_contents_string=self.file_contents_to_prompts(file_list,file_contents)
        environment_template=self.load_environment_template()
        prompt_string=[
            "Given some information about a Github repository, a file structure of the repository, "
            "and a list of important files and file contents of a repository, your task is to "
            "create a shell script that configure and set up external environments for the repository and possibly install the packages in the repository if available.",
            "Here is the information about the repository:",
            repository_information,
            "Here is the file structure of the repository:",
            repository_structure,
            "Here is a list of important files and file contents of the repository:"]
        prompt_string+=file_contents_string
        prompt_string+=["Here is the template for the shell script:",
                        environment_template,
                        "In the template:",
                        f"Replace <environment_name> with {environment_name}.",
                        "Replace <python_version> with a suitable version of Python.",
                        "Fill in the script for Step 4: Install external packages for the repository and packages in the repository."
                        "If the repository has no external packages dependencies, the script can skip installing external packages for the repository. "
                        "If the repository has no packages in itself, the script can skip installing the packages in the repository. "
                        "If the external packages for the repository and the packages in the repository can be installed together, the script should combine the commands. "
                        "Available commands for installing external packages for the repository and packages in the repository include conda install, pip install, python3, and git clone. "
                        "The packages in the repository should be installed in development mode. "
                        "The installation should ignore packages for documentation or GUI. ",
                        "Your answer should only be the shell script, not any introduction, explanation, or context.",
                        "Here is the shell script:"]

        self.prompt = self.prompt_formatting_OpenAI(prompt_string)
