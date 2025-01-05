from __future__ import annotations

from typing import Optional, Callable
import traceback

from LLM_utils.inquiry import OpenAI_interface

from auto_github.reimplementation.repo_loader import Repo_ML
from auto_github.reimplementation.prompts import ReimplementationPromptML
from auto_github.utils.stored_info import Storage
from auto_github.utils.execution import executor_ML
from auto_github.reimplementation.sequence_tests import sequence_tests_LM


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
        target_path: str = None,
        target_name: str = None,
        external_tests: Callable[[str] , str] = None,
    ) -> None:
        self.repo_link = repo_link
        self.repo_path = repo_path
        self.mode = mode
        self.approach = approach
        self.output: Optional[str] = None
        self.overwrite_environment=True
        self.external_tests=external_tests
        self.target_path=target_path
        self.main_code_path=target_path+target_name

        self.base_environment_name="test_env"
        self.tests_by_execution=True
        self.auto_tests=False
        self.cost_accumulation = 0
        self.code_generation_failure_count={"generate_code_environment":0, "generate_code_main":0}

        self.sequence_generation_timeout=180 # in seconds
        self.sequence_generation_trial_limit=5
        self.code_generation_trial_limit=5
        self.environment_designation_file_number_limit=5
        self.main_designation_file_number_limit=10
        self.environment_designation_file_content_limit=1000 # in token count
        self.main_designation_file_content_limit=1000 # in token count
        self.code_environment_execution_time_limit=300 # in seconds
        self.code_main_execution_time_limit=600 # in seconds

        self.OpenAI_instance = OpenAI_interface(
            api_key , model=model ,timeout=self.sequence_generation_timeout,
            maximum_retry=self.sequence_generation_trial_limit , debug=debug)
        self.repo_instance = Repo_ML(repo_link, repo_path, storage_path, model=model)
        self.repo_instance.clone_repo()
        self.prompt_instance = ReimplementationPromptML(storage_path,repo_path,target_path)
        self.storage_instance = Storage(storage_path,repo_path)
        self.sequence_tests_LM_instance=sequence_tests_LM(repo_path,storage_path)
        self.executor_instance = executor_ML(repo_path)


        self.trials={"environment_designation":0,"main_designation":0,"generate_code_environment":0, "generate_code_main":0}

    def run(self,goal=None):
        if self.mode == "default" :
            self.prompt_instance.goal=goal
            self.load_basic_information()
            self.step_queues=["designate_files_environment","designate_files_main","generate_code_environment","generate_code_main"]
            self.iterator()

    def iterator(self):
        '''
        this framework supports various generation styles?
        add past histories
        '''
        while self.step_queues != [] and not self.failure_trigger():
            test_status, traceback_results=self.operator()
            if test_status:
                self.step_queues.pop(0)
            else:
                self.code_generation_failure_count[self.step_queues[0]]+=1
                self.arrange_queues()
        print("--------All steps have been completed!--------")

    def failure_trigger(self):
        if self.code_generation_failure_count["generate_code_environment"] >= self.code_generation_trial_limit:
            print(f"code generation failed for setting up environment for more than {self.code_generation_trial_limit} times, aborting")
            return True
        if self.code_generation_failure_count["generate_code_main"] >= self.code_generation_trial_limit:
            print(f"code generation failed for adapting the repository for more than {self.code_generation_trial_limit} times, aborting")
            return True
        return False

    def arrange_queues(self):

        self.prompt_instance.arrange_queues_prompt()
        extraction = self.send_inquiry(tests=self.sequence_tests_LM_instance.arrange_queues_tests)

        current_step=self.step_queues[0]
        if current_step=="generate_code_environment":
            if extraction=="designate_files_environment":
                self.step_queues.insert(0,"designate_files_environment")
        if current_step=="generate_code_main":
            if extraction=="designate_files_environment":
                self.step_queues.insert(0,"designate_files_environment")
                self.step_queues.insert(1,"generate_code_environment")
            if extraction=="generate_code_environment":
                self.step_queues.insert(0,"generate_code_environment")
            if extraction=="designate_files_main":
                self.step_queues.insert(0,"designate_files_main")

    def operator(self):
        test_status=True
        traceback_results="N/A"
        current_step=self.step_queues[0]
        if current_step=="designate_files_environment":
            self.trials["environment_designation"] += 1
            trial=self.trials["environment_designation"]
            print("--------begin designating files for setting up the environment--------")
            self.designate_files_environment()
        if current_step=="designate_files_main":
            self.trials["main_designation"] += 1
            trial=self.trials["main_designation"]
            print("--------begin designating files for adapting the repository--------")
            self.designate_files_main()
        if current_step=="generate_code_environment":
            self.trials["generate_code_environment"] += 1
            trial=self.trials["generate_code_environment"]
            print("--------begin generating shell script for setting up the environment--------")
            test_status,traceback_results=self.generate_code_environment()
        if current_step=="generate_code_main":
            self.trials["generate_code_main"] += 1
            trial=self.trials["generate_code_main"]
            print("--------begin generating Python code for adapting the repository--------")
            test_status,traceback_results=self.generate_code_main()

        self.storage_instance.add_history(current_step,trial,test_status,traceback_results)
        return test_status,traceback_results

    def send_inquiry(self,tests=None):
        if tests:
            response, cost = self.OpenAI_instance.ask_with_test(self.prompt_instance.prompt , tests, self.sequence_generation_trial_limit)
        else:
            response, cost = self.OpenAI_instance.ask(self.prompt_instance.prompt)
        self.cost_accumulation += cost
        return response

    @staticmethod
    def auto_load_save(method) :
        """
        Decorator to automatically call self.load_info() before the method
        and self.save_info() after the method.

        Currently, the method is inactive
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

    def designate_files_environment(self):
        self.prompt_instance.designate_files_environment_prompt()
        extraction=self.send_inquiry(tests=self.sequence_tests_LM_instance.designate_files_tests)
        self.storage_instance.add_entries("environment_designation" , extraction , self.trials["environment_designation"])

    def designate_files_main(self ):
        self.prompt_instance.designate_files_main_prompt()
        extraction=self.send_inquiry(tests=self.sequence_tests_LM_instance.designate_files_tests)
        self.storage_instance.add_entries("main_designation" , extraction , self.trials["main_designation"])

    def generate_code_environment(self):
        if self.overwrite_environment:
            self.environment_name=self.base_environment_name
        else:
            self.environment_name = self.base_environment_name+str(self.trials["generate_code_environment"])
        self.prompt_instance.environment_name=self.environment_name
        self.sequence_tests_LM_instance.environment_name=self.environment_name

        self.generate_code_environment_raw_response()
        traceback_results=None
        test_status=True
        try:
            self.generate_code_environment_tests_and_execution()
        except Exception as e:
            print("Error detected in the code for setting up the environment")
            test_status=False
            traceback_results=traceback.format_exc()
            print("Traceback results:")
            print(traceback_results)

        return test_status,traceback_results

    def generate_code_environment_raw_response(self):
        self.prompt_instance.generate_code_environments_prompt(self.trials["environment_designation"])
        raw_response = self.send_inquiry()
        self.storage_instance.add_entries("environment_code_raw",raw_response,self.trials["generate_code_environment"])

    def check_code_environment_output(self , execution_output):
        self.prompt_instance.check_code_environment_output_prompt(self.trials["generate_code_environment"] , execution_output)
        extraction = self.send_inquiry(tests=self.sequence_tests_LM_instance.check_code_environment_output_tests)
        assert extraction==True, (f"Setting up the environment failed, here is the execution output "
                                  f"from setting up the environment:\n{execution_output}")

    def generate_code_environment_tests_and_execution(self):
        self.storage_instance.load_info()
        raw_response = self.storage_instance.information[self.repo_path]['environment_code_raw'][str(self.trials["generate_code_environment"])]
        environment_code = self.sequence_tests_LM_instance.generate_code_environment_tests(raw_response)
        self.storage_instance.add_entries("environment_code",environment_code,self.trials["generate_code_environment"])
        # currently, environment_code stores strings of code that pass the basic tests but not the functionality test
        _, execution_output=self.executor_instance.create_environment(environment_code)
        self.check_code_environment_output(execution_output)

    def generate_code_main(self):

        self.generate_code_main_raw_response()
        traceback_results=None
        test_status=True
        try:
            self.generate_code_main_tests()
        except Exception as e:
            print("Error detected in the Python code for adapting the repository")
            test_status=False
            traceback_results=traceback.format_exc()
            print("Traceback results:")
            print(traceback_results)

        return test_status,traceback_results

    def generate_code_main_raw_response(self):
        self.prompt_instance.generate_code_main_prompt(self.trials["main_designation"])
        raw_response = self.send_inquiry()
        self.storage_instance.add_entries("main_code_raw",raw_response,self.trials["generate_code_main"])

    def generate_code_main_tests(self):
        self.storage_instance.load_info()
        raw_response = self.storage_instance.information[self.repo_path]['main_code_raw'][str(self.trials["generate_code_main"])]
        main_code = self.sequence_tests_LM_instance.generate_code_main_tests(
            raw_response, self.target_path, self.main_code_path, self.tests_by_execution, self.external_tests, self.auto_tests)
        self.storage_instance.add_entries("main_code",main_code,self.trials["generate_code_main"])

    #TODO: add prompt length and file suggestion number restriction
    #TODO: unify the type of trials?
    #TODO: add shell script and code execution time limit
    #TODO: tests for situations where retry is triggered