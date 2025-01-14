from __future__ import annotations

from LLM_utils.prompter import PromptBase
from LLM_utils.prompter import available_packages_prompt
from LLM_utils.cost import Calculator
from auto_github.utils.stored_info import Storage
import os

class ReimplementationPromptML(PromptBase):
    module_dir = os.path.dirname(os.path.abspath(__file__))

    template_relative_path = "environment_template.sh"

    environment_template_path = os.path.join(module_dir , template_relative_path)

    def __init__(self, model, environment_designation_file_number_limit, main_designation_file_number_limit,
                 environment_designation_file_content_limit, main_designation_file_content_limit,
                 feedback_content_limit,storage_path, repo_path, target_path, hardware_accelerator,goal=None) -> None:

        self.storage_instance=Storage(storage_path,repo_path)
        self.repo_path=repo_path
        self.target_path=target_path
        self.goal=goal
        self.calculator_instance=Calculator(model=model)
        self.environment_name=None
        self.environment_designation_file_number_limit=environment_designation_file_number_limit
        self.main_designation_file_number_limit=main_designation_file_number_limit
        self.environment_designation_file_content_limit=environment_designation_file_content_limit # in token count
        self.main_designation_file_content_limit=main_designation_file_content_limit # in token count
        self.feedback_content_limit=feedback_content_limit
        self.hardware_accelerator=hardware_accelerator


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
            "Given a programming goal, some information about the repository, "
            "a file structure of a Github repository, and available hardware accelerators, "
            "your task is to designate the files that are "
            "important to reference to achieve the goal.",
            "Here is the programming goal:" ,
            goal,
            "Here is the information about the repository:",
            repository_information,
            "Here is the file structure of the repository:",
            repository_structure,
            f"Here is the list of available hardware accelerators:",
            f"{self.hardware_accelerator}"
            ]


        if self.check_retry(prompt_type):
            step , trial , _ , feedback , code = self.storage_instance.load_history()
            history_string = self.history_to_prompts(step , feedback , code)
            previous_response_trial=self.storage_instance.get_latest_trial(prompt_type)
            if prompt_type=="environment_designation":
                previous_response = self.storage_instance.load_common_info(
                    file_list_environment=True , trial_designation=previous_response_trial)
            if prompt_type=="main_designation":
                previous_response=self.storage_instance.load_common_info(file_list_main=True, trial_designation=previous_response_trial)

            previous_response=previous_response["file_list"]

            prompt_string+=history_string
            prompt_string+=[f"Your previous answer is as below:\n{previous_response}",
                            "Your goal this time is to suggest different files to examine. "
                            "But your suggested files should still be included in the repository"
                            " (as mentioned in the file structure of the repository) and "
                            "there can be some overlap with your previous suggestions."]
            if prompt_type=="environment_designation":
                prompt_string+=["You should consider the traceback results carefully for your answer this time. "]
            if prompt_type=="main_designation":
                prompt_string+=["You answer this time should at least include the critical files involved the traceback results to examine. "]

        prompt_string+=["Your answer should be a Python list of strings. Your answer should not include any introduction, explanation, or context."]

        if prompt_type=="environment_designation":
            prompt_string += [
                f"The Python list of strings should contain at most {self.environment_designation_file_number_limit}"
                f" elements (at most {self.environment_designation_file_number_limit} suggested files"
                f" for configuring and setting up external environment)."]
        if prompt_type=="main_designation":
            prompt_string += [
                f"The Python list of strings should contain at most {self.main_designation_file_number_limit}"
                f" elements (at most {self.main_designation_file_number_limit} suggested files"
                f" for achieving the goal)."]
        prompt_string+=[
            "Here is the Python list of string, with each string representing an the file"
            " path (starting with 'repo_root/') and file name of an important file for "+response_header,]

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

    def file_contents_to_prompts(self, file_list_type: str, file_list: list[str] , file_contents:dict[str,str]):
        file_contents_string=[]
        for file in file_list:
            file_contents_string+=([f"-----File path and file name:{file}-----"])
            content=file_contents[file]
            if file_list_type=="generate_code_environment":
                content=self.calculator_instance.length_limiter([content],self.environment_designation_file_content_limit)
            if file_list_type=="generate_code_main":
                content=self.calculator_instance.length_limiter([content],self.main_designation_file_content_limit)
            file_contents_string+=["File content:"]
            file_contents_string+=content
            file_contents_string+=["\n"]
        return file_contents_string

    def load_environment_template(self):
        with open(ReimplementationPromptML.environment_template_path, "r") as file:
            environment_template = file.read()
        return environment_template

    def generate_code_environments_prompt(self , trial_environment_designation):

        loaded_info=self.storage_instance.load_common_info(file_contents=True , repository_structure=True , repository_information=True , file_list_environment=True , trial_designation=trial_environment_designation)
        file_contents, repository_structure,repository_information, file_list = loaded_info['file_contents'], loaded_info['repository_structure'],loaded_info['repository_information'],loaded_info['file_list']

        file_contents_string=self.file_contents_to_prompts("generate_code_environment",file_list,file_contents)
        environment_template=self.load_environment_template()


        prompt_string=[
            "Given a programming goal, some information about a Github repository, a file structure of the repository, "
            "a list of important files and file contents of a repository, and available hardware accelerators, your task is to "
            "create a shell script that configure and set up external environment for utilizing the repository to achieve the programming goal "
            "and possibly install the packages in the repository if available.",
            "Here is the programming goal:" ,
            self.goal ,
            "Here is the information about the repository:",
            repository_information,
            "Here is the file structure of the repository:",
            repository_structure,
            "The working directory for the shell script is the repository's root directory (repo_root)",
            "Here is a list of important files and file contents of the repository:"]
        prompt_string+=file_contents_string
        prompt_string+=[f"Here is the list of available hardware accelerators:",
                        f"{self.hardware_accelerator}"]
        prompt_string+=["Here is the template for the shell script:",
                        environment_template,
                        "In the template:",
                        f"Replace <environment_name> with {self.environment_name}.",
                        "Replace <python_version> with a suitable version of Python.",
                        "Fill in the script for Step 4: Install external packages for the repository and packages in the repository."
                        "If the repository has no external packages dependencies, the script can skip installing external packages for the repository. "
                        "If the repository has no packages in itself, the script can skip installing the packages in the repository. "
                        "If the external packages for the repository and the packages in the repository can be installed together, the script should combine the commands. "
                        "Available commands for installing external packages for the repository and packages in the repository include conda install, pip install, python, and git clone. "
                        "The packages in the repository should be installed in development mode."
                        "Each package to be installed should consider the available hardware accelerators. For example, install the GPU-versions of the packages if GPU is available."
                        "The installation should ignore packages for documentation or GUI. "]

        if self.check_retry("environment_code_raw"):
            step , trial , _ , feedback , code = self.storage_instance.load_history()
            history_string = self.history_to_prompts(step , feedback , code)
            prompt_string += history_string
            prompt_string += ["Your goal is to generate a different shell script for configuring and setting up external environment to achieve the programming goal.",
                              "You should consider the traceback results and the list of important files and file contents of the repository for your answer. ",
                              "The shell script in your answer should be different from the shell script that failed" ]

        prompt_string+=["Your answer should only be the shell script, not any introduction, explanation, or context.",
                        "Your script should not reference to any files not in the repository (as shown in the file structure of the repository)(without downloading the files).",
                        "Here is the shell script:"]

        self.prompt = PromptBase.list_to_formatted_OpenAI(prompt_string)

    def check_code_environment_output_prompt(self , trial_designation , execution_output):

        self.storage_instance.load_info()
        script = self.storage_instance.information[self.repo_path]['environment_code'][str(trial_designation)]
        prompt_string=[
            "Given programing goal, a shell script, available hardware accelerators, and the execution"
            " output of the shell script for setting up and configuring the environment of a project"
            ", your task is to classify if the environment was set up successfully"
            " for the programming goal.",
            "Here is the programming goal:",
            self.goal,
            "Here is the shell script:",
            script,
            "Here is the list of available hardware accelerators:",
            f"{self.hardware_accelerator}",
            "Here is the execution output of the shell script:",
            execution_output,
            "You should check: 1. whether there is any errors or failures in the process. "
            "2. whether there are any packages that have versions for utilizing efficient hardware accelerators "
            "but are installed with the versions that do not utilize the accelerators, such as GPU (if available)."
            "3. any timeout during installation or downloading of packages. ",
            "You should ignore: non-critical warnings.",
            "Your answer should be a Python boolean value (True or False). Your answer should not include any introduction, explanation, or context.",
            "Here is the Python boolean value:"]
        self.prompt = PromptBase.list_to_formatted_OpenAI(prompt_string)

    def generate_code_main_prompt(self, trial_main_designation):
        loaded_info=self.storage_instance.load_common_info(file_contents=True , repository_structure=True , repository_information=True , file_list_main=True , trial_designation=trial_main_designation)
        file_contents, repository_structure,repository_information, file_list = loaded_info['file_contents'], loaded_info['repository_structure'],loaded_info['repository_information'],loaded_info['file_list']


        file_contents_string=self.file_contents_to_prompts("generate_code_main",file_list,file_contents)
        prompt_string=[
            "Given some information about a Github repository, a file structure of the repository, "
            "a list of important files and file contents of a repository, the installed packages in the environment, "
            "and available hardware accelerators, your task is to "
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
        prompt_string+=[f"Here is the list of available hardware accelerators:",
                        f"{self.hardware_accelerator}"]

        if not self.check_retry("main_code_raw"):
            prompt_string+=[f"The programming goal is:\n{self.goal}"]

        prompt_string+=["Your answer can import modules from the repository, "
                        "adapt existing code in the repository, utilize installed packages from the Conda environment, "
                        "and incorporate new code. Your answer should utilize the available hardware accelerators, such as GPU (if available)).",]

        if self.check_retry("main_code_raw"):
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

        feedback=self.calculator_instance.length_limiter([feedback],self.feedback_content_limit)

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
            history_string+=feedback
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
                        "Available steps are: "
                        "1. 'designate_files_environment': decide which files to look at for "
                        "configuring and setting up external environment. Your answer should be "
                        "this one if the environment setup is incorrect and examining additional "
                        "files for configuring and setting up external environment is critical. "
                        "2. 'designate_files_main': decide which files to look at for adapting the code from the repository. "
                        "Your answer should be this one if the environment setup is correct and "
                        "examining additional files for adapting the code from the repository is critical. "
                        "3. 'generate_code_environment': regenerate the shell script for configuring and setting up external environment. "
                        "Your answer should be this one if the environment setup is incorrect but "
                        "examining additional files for configuring and setting up external environment is not needed. "
                        "4. 'generate_code_main': regenerate the Python code for adapting the code from the repository. "
                        "Your answer should be this one if the environment setup is correct and "
                        "examining additional files for adapting the code from the repository is not needed."]

        prompt_string+= ["Your answer should be a Python string (one of 'designate_files_environment' "
                         "'designate_files_main', 'generate_code_environment', and 'generate_code_main') "
                         "Your answer may or may not be the same as the previous step. "
                         "Your answer should not include any introduction, explanation, or context.",
                         "Here is the Python string:"]

        self.prompt = PromptBase.list_to_formatted_OpenAI(prompt_string)