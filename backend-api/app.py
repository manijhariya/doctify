from fastapi import FastAPI
from pydantic import BaseModel

from llm import get_replicate_llm_output

app = FastAPI()

class GetDocsString(BaseModel):
    languageId : str
    commented :bool = True
    source : str
    #context : str | None
    #width : float | None
    code : str
    #location: int | None
    #line : str | None


@app.post("/generate_docs")
def get_new_text(generate_docs_string : GetDocsString):
    generate_docs_json = generate_docs_string.dict() 
    docstring = get_replicate_llm_output(generate_docs_json['code'], generate_docs_json['languageId'])
    return {"docstring" : docstring, "position" : "below","cursorMarker" : None}


@app.post("/get_sample_output")
def get_sample_out():
    return {"docstring" : "A" * 20, "position" : "below", "cursorMarker" : None }
