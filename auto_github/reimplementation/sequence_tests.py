from LLM_utils.inquiry import extract_code
from LLM_utils.storage import save_python_code
from auto_github.utils.stored_info import Storage
from typing import Any,Callable
import re

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

    def generate_code_environment_tests(self , raw_sequence) :
        """
        Validate the generated shell script to ensure it only uses allowed commands,
        contains the required `conda create -n self.environment_name` and `conda activate self.environment_name` commands,
        and checks whether the active environment matches `self.environment_name`.

        Args:
            raw_sequence (str): The raw shell script as a string.

        Raises:
            AssertionError: If the script contains invalid commands, syntax, or is missing required commands.
        """
        code = extract_code(raw_sequence , language="bash")

        # Define the allowed commands and their patterns
        allowed_commands = {
            r'conda create -n \w+ .*' : "conda create" ,
            # Allow any arguments after `conda create -n <env_name>`
            r'conda activate \w+' : "conda activate" ,  # Allow only `conda activate <env_name>`
            r'conda install .*' : "conda install" ,  # Allow any arguments after `conda install`
            r'pip install .*' : "pip install" ,  # Allow any arguments after `pip install`
            r'python .*' : "python" ,  # Allow any arguments after `python`
            r'git clone .*' : "git clone" ,  # Allow any arguments after `git clone`
            r'echo "Setup complete!"' : "echo" ,  # Exact match for this specific echo command
            r'current_env=\$\(conda info --envs \| grep \'\*\' \| awk \'\{print \$1\}\'\)' : "current_env assignment" ,
            r'if \[ "\$current_env" != "\w+" \]; then' : "if condition" ,
            r'echo "Error: The active environment is not \'\w+\'. Please activate the correct environment and rerun the script."' : "error message" ,
            r'exit 1' : "exit" ,
            r'fi' : "fi" ,  # Add pattern for 'fi'
            r'then' : "then" ,  # Add pattern for 'then'
            }

        # Split the script into lines
        lines = code.strip().split('\n')

        # Flags to check if required commands are present
        has_conda_create = False
        has_conda_activate = False
        has_current_env_check = False

        # Iterate through each line and check if it matches any allowed command
        i = 0
        while i < len(lines) :
            line = lines[i].strip()
            if not line or line.startswith('#') :  # Skip empty lines and comments
                i += 1
                continue

            # Check if the line starts a multi-line command (e.g., `pip install -r <(echo "...")`)
            if line.startswith("pip install -r <(echo") :
                # Combine the multi-line command into a single block
                multi_line_command = line
                i += 1
                while i < len(lines) and not lines[i].strip().endswith('")') :
                    multi_line_command += " " + lines[i].strip()
                    i += 1
                if i < len(lines) :
                    multi_line_command += " " + lines[i].strip()
                    i += 1

                # Validate the multi-line command as a single unit
                matched = False
                for pattern , command in allowed_commands.items() :
                    if re.fullmatch(pattern , multi_line_command) :
                        matched = True
                        break
                assert matched , f"Invalid command or syntax: {multi_line_command}"
                continue

            # For single-line commands, validate as usual
            matched = False
            for pattern , command in allowed_commands.items() :
                if re.fullmatch(pattern , line) :
                    matched = True
                    # Check if the line contains `conda create -n self.environment_name`
                    if f"conda create -n {self.environment_name}" in line :
                        has_conda_create = True
                    # Check if the line contains `conda activate self.environment_name`
                    elif f"conda activate {self.environment_name}" in line :
                        has_conda_activate = True
                    # Check if the line contains the current environment check logic
                    elif f'if [ "$current_env" != "{self.environment_name}" ]; then' in line :
                        has_current_env_check = True
                    break

            # Use assert to validate the line
            assert matched , f"Invalid command or syntax: {line}"
            i += 1

        # Ensure `conda create -n self.environment_name` and `conda activate self.environment_name` are present
        assert has_conda_create , f"The script is missing the 'conda create -n {self.environment_name}' command."
        assert has_conda_activate , f"The script is missing the 'conda activate {self.environment_name}' command."
        assert has_current_env_check , f"The script is missing the check for the active environment: 'if [ \"$current_env\" != \"{self.environment_name}\" ]; then'."
        return code

    def generate_code_main_tests(self ,
                                 raw_sequence: str ,
                                 target_path: str ,
                                 target_name: str ,
                                 tests_by_execution:bool = True ,
                                 external_tests_path: str = None ,
                                 auto_tests:bool = False):

        code = extract_code(raw_sequence)
        save_python_code(code, target_path+target_name)


        if tests_by_execution:
            return_code , tests_by_execution_output=self.executor_instance.execute_main_code(target_path,target_name,self.environment_name)
            assert return_code== 0, f"Tests failed, code execution output: {tests_by_execution_output}"

        if external_tests_path is not None:
            print("-----performing external tests-----")

            return_code, external_test_output=self.executor_instance.execute_main_code(target_path, external_tests_path, environment_name=self.environment_name)
            assert return_code== 0, f"Tests failed, code execution output: {external_test_output}"

        # TODO: implement auto_tests

        return code

    def arrange_queues_tests(self , raw_sequence) :

        # Remove extra single quotes and whitespace, then convert to lowercase
        raw_sequence = raw_sequence.strip("'\" \n\r\t").lower()

        assert (raw_sequence in
                ["designate_files_environment" , "designate_files_main" ,
                 "generate_code_environment" , "generate_code_main"]) , \
            (f"the response is {raw_sequence} instead one of the following options: "
             f"designate_files_environment,designate_files_main,generate_code_environment,generate_code_main")

        return raw_sequence

if __name__ == "__main__":
    # Create an instance of the sequence_tests_LM class
    repo_path = "example_repo"
    environment_name = "myenv"  # Set the environment name
    test_instance = sequence_tests_LM(repo_path, environment_name=environment_name)

    # Example shell script to test
    valid_script = f"""
    #!/bin/bash
    conda create -n {environment_name} python=3.9 -y
    conda activate {environment_name}
    current_env=$(conda info --envs | grep '*' | awk '{{print $1}}')
    if [ "$current_env" != "{environment_name}" ]; then
        echo "Error: The active environment is not '{environment_name}'. Please activate the correct environment and rerun the script."
        exit 1
    fi
    python main.py
    pip install -r <(echo "
    absl-py
    babel
    editdistance
    immutabledict
    gin-config
    mesh-tensorflow[transformer] @ git+https://github.com/tensorflow/mesh#egg=mesh-tensorflow
    nltk
    numpy
    pandas<2.0.0
    rouge-score>=0.1.2
    sacrebleu
    scikit-learn
    scipy
    sentencepiece
    seqio-nightly
    six>=1.14
    tfds-nightly
    transformers>=2.7.0
    ")
    """

    # Test the generate_code_environment_tests method
    try:
        print("Testing valid script...")
        validated_code = test_instance.generate_code_environment_tests(valid_script)
        print("Test passed! Validated code:")
        print(validated_code)
    except AssertionError as e:
        print(f"Test failed: {e}")

    # Example of an invalid script (missing conda activate)
    invalid_script = f"""
    conda create -n {environment_name} python=3.8 -y
    conda install numpy pandas -y
    pip install -e .
    pip install requests
    git clone https://github.com/example/repo.git
    echo "Setup complete!"
    """

    # Test the generate_code_environment_tests method with an invalid script
    try:
        print("\nTesting invalid script (missing conda activate)...")
        validated_code = test_instance.generate_code_environment_tests(invalid_script)
        print("Test passed! Validated code:")
        print(validated_code)
    except AssertionError as e:
        print(f"Test failed (expected): {e}")

    # Example of another invalid script (invalid environment name)
    invalid_script_2 = """
    conda create -n wrongenv python=3.8 -y
    conda activate wrongenv
    conda install numpy pandas -y
    pip install -e .
    pip install requests
    git clone https://github.com/example/repo.git
    echo "Setup complete!"
    """

    # Test the generate_code_environment_tests method with another invalid script
    try:
        print("\nTesting invalid script (invalid environment name)...")
        validated_code = test_instance.generate_code_environment_tests(invalid_script_2)
        print("Test passed! Validated code:")
        print(validated_code)
    except AssertionError as e:
        print(f"Test failed (expected): {e}")