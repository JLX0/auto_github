# Currently under active development

- Documentations and more examples will be added soon.
- Currently, supports machine learning repos that are mainly written in Python and can be setup with `conda` and `pip`.
- Example usage is available.

# Auto-Github
Automatically complete tasks related to Github with LLMs etc.

# Requirements

OS: Linux-based

Python: >= 3.10

`conda` is installed and available.

# Installation

`git clone https://github.com/JLX0/auto_github.git`

`cd auto_github`

`pip install .`

# Usage

First, fill in your API keys for LLMs with your actual keys in `key.json`. You only need to fill in at least one type of key.

Then, see `examples` (more will be added soon).

If you want to use OpenAI models, change the argument `target_key` in `get_api_key` and `model` in `AutoReimplementation` accordingly.


