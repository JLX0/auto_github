from LLM_utils.inquiry import extract_Python
from auto_github.utils.stored_info import Storage


class sequence_tests_LM():
    def __init__(self, repo_path, storage_path="repos.json"):
        self.repo_path = repo_path
        self.storage_instance = Storage(storage_path, repo_path)

    def designate_files_tests(self , raw_sequence):
        self.storage_instance.load_info()
        code=extract_Python(raw_sequence,mode="python_object")
        assert isinstance(code,list), f"the response is {code} instead of a Python list"
        for file_name in code:
            assert isinstance(file_name,str), f"the response is {file_name} instead of a string"
            assert file_name in self.storage_instance.information[self.repo_path]['file_contents'], f"the file {file_name} is not in the loaded files"
        return code
