from __future__ import annotations

from typing import Optional

from LLM_utils.prompter import PromptBase


class ReimplementationPrompt(PromptBase):

    def designate_files(self,
                        repository_structure: str,
                        goal: str,
                        repository_information: str,
                        ):
        prompt_string = [
            "Given a file structure of a Github repository, a goal of writing code, and some "
            "information about the repository, your task is to designate the files that are "
            "important to reference to achieve the goal.",
            "Here is the file structure of the repository:",
            repository_structure,
            "Here is the goal of writing code:",
            goal,
            "Here is some information about the repository:",
            repository_information,
            "Here is the list of important files:",
        ]
        self.prompt = self.prompt_formatting_OpenAI(prompt_string)