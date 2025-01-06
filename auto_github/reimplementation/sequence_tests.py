from LLM_utils.inquiry import extract_code
from LLM_utils.storage import save_python_code
from auto_github.utils.stored_info import Storage
from typing import Any,Callable

from auto_github.utils.execution import executor_ML


class sequence_tests_LM():
    def __init__(self, repo_path, storage_path="repos.json", environment_name=None, code_environment_execution_time_limit=300, code_main_execution_time_limit=500):
        self.repo_path = repo_path
        self.storage_instance = Storage(storage_path, repo_path)
        self.executor_instance = executor_ML(repo_path,code_environment_execution_time_limit, code_main_execution_time_limit)
        self.environment_name=environment_name

    def set_files_limit(self,environment_designation_file_number_limit=None,main_designation_file_number_limit=None):
        self.environment_designation_file_number_limit=environment_designation_file_number_limit
        self.main_designation_file_number_limit=main_designation_file_number_limit

    def designate_files_tests(self , raw_sequence):
        self.storage_instance.load_info()
        code=extract_code(raw_sequence,mode="python_object")
        assert isinstance(code,list), f"the response is {code} instead of a Python list"
        if self.environment_designation_file_number_limit is not None:
            assert len(code) <= self.environment_designation_file_number_limit, f"the response contains {len(list)} files, but the limit is {self.environment_designation_file_number_limit}"
        if self.main_designation_file_number_limit is not None:
            assert len(code) <= self.main_designation_file_number_limit, f"the response contains {len(list)} files, but the limit is {self.main_designation_file_number_limit}"
        for file_name in code:
            assert isinstance(file_name,str), f"the response is {file_name} instead of a string"
            assert file_name in self.storage_instance.information[self.repo_path]['file_contents'], f"the file {file_name} is not in the loaded files"
        return code

    def check_code_environment_output_tests(self , raw_sequence):
        code = extract_code(raw_sequence , mode="python_object")
        assert isinstance(code,bool), f"the response is {code} instead of a boolean"
        return code

    def generate_code_environment_tests(self, raw_sequence):
        code = extract_code(raw_sequence, language="bash")
        # TODO: complete the tests with asserts
        return code

    def generate_code_main_tests(self,
                                 raw_sequence: str,
                                 target_path: str ,
                                 main_code_path: str,
                                 tests_by_execution:bool = True,
                                 external_tests: Callable[[str] , str] = None,
                                 auto_tests:bool = False):

        code = extract_code(raw_sequence)
        save_python_code(code, main_code_path)

        outputs: dict[str , str|None] = {
            "tests_by_execution_output" : None ,
            "external_tests_output" : None ,
            "auto_tests_output" : None
            }

        if tests_by_execution:
            _ , tests_by_execution_output=self.executor_instance.execute_main_code(target_path,main_code_path,self.environment_name)
            outputs["tests_by_execution_output"]=tests_by_execution_output

        if external_tests is not None:
            print("-----performing external tests-----")
            external_tests_output = external_tests(code)
            outputs["external_tests_output"]=external_tests_output
            # some tests might not require input arguments and directly import from local files?

        # TODO: implement auto_tests

        if auto_tests or tests_by_execution or external_tests is not None :
            return code,outputs
        else:
            return code

    def arrange_queues_tests(self,raw_sequence):
        print("raw_sequence:",raw_sequence)
        print("raw_sequence type:",type(raw_sequence))
        # TODO: there seems to be an error for this test
        assert (raw_sequence in
                ["designate_files_environment","designate_files_main","generate_code_environment","generate_code_main"]),\
            (f"the response is {raw_sequence} instead one of the following options: "
             f"designate_files_environment,designate_files_main,generate_code_environment,generate_code_main")
        return raw_sequence