# Doctify - Vscode extension for generating docstring for python code.

export replicate api token in enviornment variable 
```
export REPLICATE_API_TOKEN=<paste-your-token-here>
```

## Start Local Python server
-*- We are using replicate for now but will try to build it using local finetuned llm.
Change into backend-api directory
#### Install requirements.txt 
```
python -m pip install -r requirements.txt
```

#### Run server
```
uvicorn app:app --port 5000
```

## For now you can test this using vscode debug mode.
