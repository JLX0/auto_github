import subprocess

# Command to clear PYTHONPATH, activate the environment, and run pip list
command = """
unset PYTHONPATH && eval "$(conda shell.bash hook)" && conda activate optuna && pip list && python3 -c "import optuna; print(); print(optuna.__version__)"
"""

# Run the command
process = subprocess.Popen(command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

print("Output:", stdout.decode())
print("Error:", stderr.decode())