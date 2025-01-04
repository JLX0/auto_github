import ConfigSpace as CS
import ConfigSpace.hyperparameters as CSH
import numpy as np

from main_code.py import *

# Define a simple configuration space
def create_configspace():
    cs = CS.ConfigurationSpace()
    cs.add_hyperparameter(CSH.UniformFloatHyperparameter('x', lower=-5, upper=5))
    cs.add_hyperparameter(CSH.UniformFloatHyperparameter('y', lower=-5, upper=5))
    return cs

# Define a simple fitness function
def fitness_function(config, budget):
    x = config['x']
    y = config['y']
    # Example: minimize the Rosenbrock function
    loss = (1 - x)**2 + 100 * (y - x**2)**2
    return loss

# Test the load_BOHB function
def test_load_BOHB():
    # Create the configuration space
    configspace = create_configspace()

    # Load BOHB with the configuration space
    run_BOHB = load_BOHB(configspace, eta=3, min_budget=0.01, max_budget=1)

    # Run BOHB with the fitness function
    best_config = run_BOHB(fitness_function)

    # Print the best configuration found
    print("Best Configuration:", best_config)

    # Evaluate the fitness function at the best configuration
    best_loss = fitness_function(best_config, budget=1)
    print("Best Loss:", best_loss)

test_load_BOHB()