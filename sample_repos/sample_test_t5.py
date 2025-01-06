import unittest
import torch
from main_code import load_T5

class TestLoadT5(unittest.TestCase):
    def test_load_T5_returns_module(self):
        # Define some hyperparameters for testing
        hyperparams = {
            'model_name': 't5-small',
            'num_layers': 6,
            'num_heads': 8,
            'd_model': 512,
            'd_ff': 2048,
            'dropout_rate': 0.1,
            'vocab_size': 32128
        }

        # Call the load_T5 function
        model = load_T5(**hyperparams)

        # Check if the returned object is an instance of torch.nn.Module
        self.assertIsInstance(model, torch.nn.Module)

    def test_load_T5_forward_pass(self):
        # Define some hyperparameters for testing
        hyperparams = {
            'model_name': 't5-small',
            'num_layers': 6,
            'num_heads': 8,
            'd_model': 512,
            'd_ff': 2048,
            'dropout_rate': 0.1,
            'vocab_size': 32128
        }

        # Call the load_T5 function
        model = load_T5(**hyperparams)

        # Create a dummy input batch
        batch_size = 2
        seq_length = 10
        input_ids = torch.randint(0, hyperparams['vocab_size'], (batch_size, seq_length))
        attention_mask = torch.ones((batch_size, seq_length), dtype=torch.long)

        # Perform a forward pass
        output = model(input_ids=input_ids, attention_mask=attention_mask)

        # Check if the output is a tensor
        self.assertIsInstance(output, torch.Tensor)

if __name__ == '__main__':
    unittest.main()