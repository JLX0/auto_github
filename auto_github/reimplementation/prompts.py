from __future__ import annotations

from LLM_utils.prompter import PromptBase
from LLM_utils.prompter import available_packages_prompt

from auto_github.utils.stored_info import Storage
import os

class ReimplementationPromptML(PromptBase):
    environment_template_path = "/home/j/experiments/auto_github/auto_github/reimplementation/environment_template.sh"

    def __init__(self, storage_path, repo_path, target_path, goal=None) -> None:

        self.storage_instance=Storage(storage_path,repo_path)
        self.repo_path=repo_path
        self.target_path=target_path
        self.goal=goal

        self.environment_name=None

    def check_retry(self,prompt_type):
        self.storage_instance.load_info()
        if self.storage_instance.get_latest_trial(prompt_type) is None:
            return False
        else:
            return True

    def designate_files_prompt(self ,
                               repository_structure: str ,
                               goal: str ,
                               repository_information: str ,
                               response_header: str ,
                               prompt_type:str ,
                               ):

        prompt_string = [
            "Given a programming goal, some information about the repository, and "
            "a file structure of a Github repository, your task is to designate the files that are "
            "important to reference to achieve the goal.",
            "Here is the programming goal:" ,
            goal,
            "Here is the information about the repository:",
            repository_information,
            "Here is the file structure of the repository:",
            repository_structure]


        if self.check_retry(prompt_type):
            step , trial , _ , feedback , code = self.storage_instance.load_history()
            history_string = self.history_to_prompts(step , feedback , code)
            previous_response_trial=self.storage_instance.get_latest_trial(prompt_type)
            if prompt_type=="environment_designation":
                previous_response = self.storage_instance.load_common_info(
                    file_list_environment=True , trial_designation=previous_response_trial)
            if prompt_type=="main_designation":
                previous_response=self.storage_instance.load_common_info(file_list_main=True, trial_designation=previous_response_trial)

            prompt_string+=history_string
            prompt_string+=["Your previous answer is as below:",
                              previous_response,
                            "Your goal this time is to suggest different files to examine."]
            if prompt_type=="environment_designation":
                prompt_string+=["You should consider the traceback results carefully for your answer this time. "]
            if prompt_type=="main_designation":
                prompt_string+=["You answer this time should at least include the critical files involved the traceback results to examine. "]
            prompt_string+=["Your answer this time should be different from your previous suggestions, "
                              "although there can be some overlap. "]
        prompt_string+=[
            "Your answer should be a Python list of strings. Your answer should not include any introduction, explanation, or context.",
            "Here is the Python list of string, with each string representing an the file path (starting with 'repo_root/') and file name of an important file for "+response_header,
            ]

        self.prompt = PromptBase.list_to_formatted_OpenAI(prompt_string)

    def designate_files_environment_prompt(self):

        loaded_info=self.storage_instance.load_common_info(repository_information=True , repository_structure=True)
        repository_information, repository_structure = loaded_info['repository_information'], loaded_info['repository_structure']

        goal=("Configure and set up external environment required for the project’s core functionality,"
              " excluding documentation, GUI, and any modules or packages with source code already available in the repository.")
        repository_information=f"The content in the README.md file is as below:\n{repository_information}"
        response_header="configuring and setting up external environment:"
        self.designate_files_prompt(repository_structure , goal , repository_information , response_header,"environment_designation")

    def designate_files_main_prompt(self):

        loaded_info=self.storage_instance.load_common_info(repository_information=True , repository_structure=True)
        repository_information, repository_structure = loaded_info['repository_information'], loaded_info['repository_structure']

        goal=self.goal+"\n"+"Here are some additional context\n1. you should ignore files for documentation or GUI\n2. you should assume the external environment are already set up.\n3. the modules and packages in the repository are available and accessible (by importing for example)"
        repository_information=f"The content in the README.md file is as below:\n{repository_information}"
        response_header="achieving the goal:"
        self.designate_files_prompt(repository_structure , goal , repository_information , response_header,"main_designation")

    def file_contents_to_prompts(self, file_list: list[str] , file_contents:dict[str,str]):
        file_contents_string=[]
        for file in file_list:
            file_contents_string+=([f"-----File path and file name:{file}-----"])
            file_contents_string+=([f"File content:\n{file_contents[file]}"])
        return file_contents_string

    def load_environment_template(self):
        with open(ReimplementationPromptML.environment_template_path, "r") as file:
            environment_template = file.read()
        return environment_template

    def generate_code_environments_prompt(self , trial_environment_designation):

        loaded_info=self.storage_instance.load_common_info(file_contents=True , repository_structure=True , repository_information=True , file_list_environment=True , trial_designation=trial_environment_designation)
        file_contents, repository_structure,repository_information, file_list = loaded_info['file_contents'], loaded_info['repository_structure'],loaded_info['repository_information'],loaded_info['file_list']

        file_contents_string=self.file_contents_to_prompts(file_list,file_contents)
        environment_template=self.load_environment_template()
        prompt_string=[
            "Given some information about a Github repository, a file structure of the repository, "
            "and a list of important files and file contents of a repository, your task is to "
            "create a shell script that configure and set up external environment for the repository and possibly install the packages in the repository if available.",
            "Here is the information about the repository:",
            repository_information,
            "Here is the file structure of the repository:",
            repository_structure,
            "The working directory for the shell script is the repository's root directory (repo_root)",
            "Here is a list of important files and file contents of the repository:"]
        prompt_string+=file_contents_string
        prompt_string+=["Here is the template for the shell script:",
                        environment_template,
                        "In the template:",
                        f"Replace <environment_name> with {self.environment_name}.",
                        "Replace <python_version> with a suitable version of Python.",
                        "Fill in the script for Step 3: Install external packages for the repository and packages in the repository."
                        "If the repository has no external packages dependencies, the script can skip installing external packages for the repository. "
                        "If the repository has no packages in itself, the script can skip installing the packages in the repository. "
                        "If the external packages for the repository and the packages in the repository can be installed together, the script should combine the commands. "
                        "Available commands for installing external packages for the repository and packages in the repository include conda install, pip install, python3, and git clone. "
                        "The packages in the repository should be installed in development mode. "
                        "The installation should ignore packages for documentation or GUI. "]

        if self.check_retry("code_environment_raw"):
            step , trial , _ , feedback , code = self.storage_instance.load_history()
            history_string = self.history_to_prompts(step , feedback , code)
            prompt_string += history_string
            prompt_string += ["Your goal is to generate a different shell script for configuring and setting up external environment.",
                              "You should consider the traceback results and the list of important files and file contents of the repository for your answer. ",
                              "The shell script in your answer should be different from the shell script that failed" ]

        prompt_string+=["Your answer should only be the shell script, not any introduction, explanation, or context.",
                        "Here is the shell script:"]

        self.prompt = PromptBase.list_to_formatted_OpenAI(prompt_string)

    def check_code_environment_output_prompt(self , trial_designation , execution_output):

        self.storage_instance.load_info()
        script = self.storage_instance.information[self.repo_path]['environment_code'][str(trial_designation)]
        prompt_string=[
            "Given a shell script, and the execution output of the shell script for setting up and configuring the environment of a project"
            ", your task is to classify if the environment was set up successfully without errors or failures or not.",
            "Here is the shell script:",
            script,
            "Here is the execution output of the shell script:",
            execution_output,
            "You could ignore non-critical warnings",
            "Your answer should be a Python boolean value (True or False). Your answer should not include any introduction, explanation, or context.",
            "Here is the Python boolean value:"]
        self.prompt = PromptBase.list_to_formatted_OpenAI(prompt_string)

    def generate_code_main_prompt(self, trial_main_designation):
        loaded_info=self.storage_instance.load_common_info(file_contents=True , repository_structure=True , repository_information=True , file_list_main=True , trial_designation=trial_main_designation)
        file_contents, repository_structure,repository_information, file_list = loaded_info['file_contents'], loaded_info['repository_structure'],loaded_info['repository_information'],loaded_info['file_list']


        file_contents_string=self.file_contents_to_prompts(file_list,file_contents)
        prompt_string=[
            "Given some information about a Github repository, a file structure of the repository, "
            "and a list of important files and file contents of a repository, your task is to "
            "create Python code that satisfies a programming goal based on the packages and modules in the repository."
            "Here is the information about the repository:",
            repository_information,
            "Here is the file structure of the repository:",
            repository_structure,
            "The repository's root directory (repo_root) relative to the working directory in which the Python code will be executed is:",
            os.path.relpath(self.repo_path,self.target_path),
            "Here is a list of important files and file contents of the repository:"]
        prompt_string+=file_contents_string

        prompt_string+=available_packages_prompt(self.environment_name)

        prompt_string+=[f"The programming goal is:\n{self.goal}",
                        "Your answer can import modules from the repository, "
                        "adapt existing code in the repository, utilize installed packages from the Conda environment, "
                        "and incorporate new code. "]

        if self.check_retry("code_main_raw"):
            step , trial , _ , feedback , code = self.storage_instance.load_history()
            history_string = self.history_to_prompts(step , feedback , code)
            prompt_string += history_string
            prompt_string += ["Your goal is to generate a different Python code that satisfies a programming goal.",
                              "You should consider the traceback results and the list of important files and file contents of the repository for your answer. ",
                              "The Python code in your answer should be different from the Python code that failed" ]

        prompt_string+=["Your answer should only be the Python code, not any introduction, explanation, or context.",
                        "Here is the Python code:"]

        self.prompt = PromptBase.list_to_formatted_OpenAI(prompt_string)

    def history_to_prompts(self, step, feedback, code, mode="last_one"):
        history_string=[]
        if step == "generate_code_environment":
            step_string=("The user encountered some errors and failures in the step to"
                         " set up and configure the environment for the repository. ")
            code_name="shell script"
        if step == "generate_code_main":
            step_string=(f"The user encountered some errors and failures in the step to"
                         f" adapt the code from the repository for the following goal:\n{self.goal}")
            code_name="Python code"
        if mode=="last_one":
            history_string.append(step_string)
            history_string.append(f"Here is the {code_name} that failed:")
            history_string.append(code)
            history_string.append(f"Here is the traceback results from executing the {code_name}:")
            history_string.append(feedback)
        return history_string

    def arrange_queues_prompt(self):
        """
        currently, the past feedbacks only include the one previous step
        """

        loaded_info=self.storage_instance.load_common_info(repository_information=True , repository_structure=True)
        repository_information, repository_structure = loaded_info['repository_information'], loaded_info['repository_structure']

        step , _ , _ , feedback, code = self.storage_instance.load_history()
        history_string=self.history_to_prompts(step, feedback, code)

        prompt_string=[f"The user was trying to reimplement some functionalities in a Github repository. "]

        if step =="generate_code_main":
            prompt_string+=["Here is the goal of the user:",
                            self.goal,]

        prompt_string +=[
             "Here is the repository information:",
              repository_information,
             "Here is the repository structure:",
              repository_structure,
             "The user encountered some errors and failures in a step of the process."]

        prompt_string+= history_string

        prompt_string+=["Your task is to suggest the next step to take to fix the errors and failures.",
                        "Available steps are:"
                        "1. 'designate_files_environment': decide which files to look at for "
                        "configuring and setting up external environment. Your answer should be "
                        "this one if the environment setup is incorrect and examining additional "
                        "files for configuring and setting up external environment is critical. "
                        "2. 'designate_files_main': decide which files to look at for adapting the code from the repository. "
                        "Your answer should be this one if the environment setup is correct and "
                        "examining additional files for adapting the code from the repository is critical. "
                        "3. 'generate_code_environment': regenerate the shell script for configuring and setting up external environment. "
                        "Your answer should be this one if the environment setup is incorrect but "
                        "examining additional files for configuring and setting up external environment is not needed."
                        "4. 'generate_code_main': regenerate the Python code for adapting the code from the repository. "
                        "Your answer should be this one if the environment setup is correct and "
                        "examining additional files for adapting the code from the repository is not needed."]

        prompt_string+= ["Your answer should be a Python string (one of 'designate_files_environment' "
                         "'designate_files_main', 'generate_code_environment', and 'generate_code_main') "
                         "Your answer may or may not be the same as the previous step. "
                         "Your answer should not include any introduction, explanation, or context.",
                         "Here is the Python string:"]

        self.prompt = PromptBase.list_to_formatted_OpenAI(prompt_string)