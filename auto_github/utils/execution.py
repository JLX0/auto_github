from LLM_utils.execution import execute_bash
from LLM_utils.fault_tolerance import overtime_kill

class executor_ML:
    def __init__(self, repo_path, code_environment_execution_time_limit=300, code_main_execution_time_limit=500):
        """
        Initialize the executor_ML class.

        Args:
            repo_path: The path to the repository.
            code_environment_execution_time_limit: Time limit for environment creation in seconds.
            code_main_execution_time_limit: Time limit for main code execution in seconds.
        """
        self.repo_path = repo_path
        self.code_environment_execution_time_limit = code_environment_execution_time_limit
        self.code_main_execution_time_limit = code_main_execution_time_limit

    def create_environment_base(self, ret_dict, script, print_progress=True):
        """
        Base function to create an environment without any time limit.

        Args:
            ret_dict: Dictionary to store return values.
            script: The script to execute.
            print_progress: Whether to print progress.

        Returns:
            None
        """
        print("-----creating environments-----")
        full_script = f"""
        #!/bin/bash
        unset PYTHONPATH
        cd {self.repo_path}
        eval "$(conda shell.bash hook)"
        {script}
        """
        return_code, result = execute_bash(full_script, print_progress)

        ret_dict["return_code"] = return_code
        ret_dict["result"] = result

    def create_environment(self, script, print_progress=True):
        """
        Create an environment with a time limit using overtime_kill.

        Args:
            script: The script to execute.
            print_progress: Whether to print progress.

        Returns:
            tuple[int, str]: A tuple containing the return code and result of the script execution.
        """
        exceeded, ret_dict = overtime_kill(
            target_function=self.create_environment_base,
            target_function_args=(script, print_progress),
            time_limit=self.code_environment_execution_time_limit,
            ret=True,
        )

        if exceeded:
            print("The environment creation process was terminated due to exceeding the time limit.")
            return -1, "Environment creation timed out."

        return ret_dict.get("return_code", -1), ret_dict.get("result", "No result captured.")

    def execute_main_code_base(self, ret_dict, target_path, main_code_path, environment_name, print_progress=True):
        """
        Base function to execute the main code without any time limit.

        Args:
            ret_dict: Dictionary to store return values.
            target_path: The target path where the code will be executed.
            main_code_path: The path to the main code file.
            environment_name: The name of the conda environment to activate.
            print_progress: Whether to print progress.

        Returns:
            None
        """
        print("-----executing generated code-----")
        full_script = f"""
        #!/bin/bash
        unset PYTHONPATH
        cd {target_path}
        eval "$(conda shell.bash hook)"
        conda activate {environment_name}
        python {main_code_path}
        """
        return_code, result = execute_bash(full_script, print_progress)

        ret_dict["return_code"] = return_code
        ret_dict["result"] = result

    def execute_main_code(self, target_path, main_code_path, environment_name, print_progress=True):
        """
        Execute the main code with a time limit using overtime_kill.

        Args:
            target_path: The target path where the code will be executed.
            main_code_path: The path to the main code file.
            environment_name: The name of the conda environment to activate.
            print_progress: Whether to print progress.

        Returns:
            tuple[int, str]: A tuple containing the return code and result of the script execution.
        """
        exceeded, ret_dict = overtime_kill(
            target_function=self.execute_main_code_base,
            target_function_args=(target_path, main_code_path, environment_name, print_progress),
            time_limit=self.code_main_execution_time_limit,
            ret=True,
        )

        if exceeded:
            print("The code execution process was terminated due to exceeding the time limit.")
            return -1, "Code execution timed out."

        return ret_dict.get("return_code", -1), ret_dict.get("result", "No result captured.")


if __name__ == "__main__":
    bash_script = """
    # Step 1: Create a conda environment
    conda create -n test_1 python=3.8 -y

    # Step 2: Activate the environment
    conda activate test_1

    /home/j/miniconda3/envs/test_1/bin/pip list

    echo "Setup complete 1!"

    # Step 3: Install external packages for the repository and packages in the repository
    pip install foobooboo
    # pip install Pyro4 serpent ConfigSpace numpy statsmodels scipy netifaces

    echo "Setup complete 2!"

    # Install the repository in development mode
    # pip install -e .

    echo "Setup complete 3!"
    """

    repo_path = '/home/j/experiments/auto_github/sample_repos/bohb'  # Replace with your local repo path

    # Initialize the executor with custom time limits
    executor_ML_instance = executor_ML(
        repo_path,
        code_environment_execution_time_limit=120,  # 2 minutes for environment creation
        code_main_execution_time_limit=300,  # 5 minutes for main code execution
    )

    result_code, output = executor_ML_instance.create_environment(bash_script)
    print("result_code:", result_code)
    print("output:", output)