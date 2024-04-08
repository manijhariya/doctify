# Project Title: Doctify - Automatic Google Style Docstring Generator
 
# Description:

Developed an innovative project, Doctify, capable of generating Google style docstrings for any Python code. Leveraged state-of-the-art (STOA) technologies including the Microsoft/Phi-2 Large Language Model (LLM), enhanced with Quatizied Low Rank Adapters (QLORA) for efficient fine-tuning on a single GPU. Scraped data from popular Python libraries such as NumPy, Pandas, etc., utilizing Google style docstrings, and fine-tuned the Phi-2 model accordingly. Implemented a FastAPI backend in Python to load the model and facilitate docstring generation.

# Technologies Utilized:

    - Microsoft/Phi-2 Large Language Model (LLM)
    - Quatizied Low Rank Adapters (QLORA)
    - Python, FastAPI
    - Visual Studio Code (VSCode) Extension Development

# Key Features:

    - Integration of finetuned state-of-the-art language model for accurate docstring generation.
    - Utilization of scraped data from popular Python libraries to enhance model performance.
    - Implementation of a FastAPI backend for seamless model loading and docstring generation.

# VSCode Extension:
Additionally, developed a VSCode extension enabling seamless interaction with the FastAPI backend, allowing users to receive generated docstrings effortlessly.

# Future Scope:
Plan to release Doctify as a pip package, enabling independent usage without backend dependencies. Further, aiming to enhance functionality to generate docstrings for all Python functions within a repository with a single command, akin to black formatting.


## Installtion
```
python3 setup.py install
```

## Launching the Project
```
doctify -h
```


Call for Contributions
----------------------

The Doctify project welcomes your expertise and enthusiasm!

Small improvements or fixes are always appreciated.

Writing code isn’t the only way to contribute to Doctify. You can also:
- review pull requests
- help us stay on top of new and old issues
- develop tutorials, presentations, and other educational materials
- develop graphic design for our brand assets and promotional materials
- translate website content
- help with outreach and onboard new contributors

If you’re unsure where to start or how your skills fit in, reach out! You can
ask on GitHub, by opening a new issue or leaving a
comment on a relevant issue that is already open.

If you are new to contributing to open source, [this
guide](https://opensource.guide/how-to-contribute/) helps explain why, what,
and how to successfully get involved.