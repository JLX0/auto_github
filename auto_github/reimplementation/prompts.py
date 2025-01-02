from __future__ import annotations

from typing import Optional

from LLM_utils.prompter import PromptBase


class ReimplementationPromptML(PromptBase):

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
            response_header,
        ]
        self.prompt = self.prompt_formatting_OpenAI(prompt_string)

    def designate_files_environments(self,repository_structure,repository_information):
        goal=("Configure and set up external environments required for the project’s core functionality, "
              "excluding documentation, GUI, and any modules or packages with source code already available in the repository.")
        repository_information=f"The content in the README.md file is as below:\n{repository_information}"
        response_header="Here is the list of files for configuring and setting up external environments:"
        self.designate_files(repository_structure,goal,repository_information,response_header)

    def designate_files_main(self,goal,repository_structure,repository_information):
        goal+=goal+"\n"+"Here are some additional context\n1. you should ignore files for documentation or GUI\n2. you should assume the external environments are already set up.\n3. the modules and packages in the repository are available and accessible (by importing for example)"
        repository_information=f"The content in the README.md file is as below:\n{repository_information}"
        response_header="Here is the list of important files for achieving the goal:"
        self.designate_files(repository_structure,goal,repository_information,response_header)
