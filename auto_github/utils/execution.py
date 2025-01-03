from LLM_utils.execution import execute_bash

class executor_ML:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def create_environments(self, script, print_progress=True):
        print("-----creating environments-----")
        full_script = f"""
        #!/bin/bash
        unset PYTHONPATH
        cd {self.repo_path}
        eval "$(conda shell.bash hook)"
        {script}
        """
        return_code, result = execute_bash(full_script, print_progress)
        return return_code, result



if __name__ == "__main__":
    bash_script = """
    # Step 1: Create a conda environment
    conda create -n test_1 python=3.8 -y
    
    # Step 2: Activate the environment
    conda activate test_1
    
    echo "Current environment: $CONDA_DEFAULT_ENV"
    which python
    which pip
    export PATH="/home/j/miniconda3/envs/test_1/bin:/home/j/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    echo $PATH
    /home/j/miniconda3/envs/test_1/bin/pip list
    
    echo "Setup complete 1!"
    
    # Step 3: Install external packages for the repository and packages in the repository
    pip install Pyro4 serpent ConfigSpace numpy statsmodels scipy netifaces
    
    echo "Setup complete 2!"
    
    # Install the repository in development mode
    pip install -e .
    
    echo "Setup complete 3!"
    """

    repo_path = '/home/j/experiments/auto_github/sample_repos/bohb'  # Replace with your local repo path

    executor_ML_instance=executor_ML(repo_path)

    result=executor_ML_instance.create_environments(bash_script)