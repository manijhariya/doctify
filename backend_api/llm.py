import replicate
from src.inference import Inference

from backend_api import config, prompts

if config.load_local:
    inference = Inference(config.model_path)

REPLICATE_EP = "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3"


def get_replicate_llm_output(code, language):
    """
     Get the output of the LLM.

    Parameters
    ----------
    code : str
        The code to run.
    language : str
        The language to run the code in.

    Returns
    -------
    str
        The output of the LLM.
    """

    prompt = prompts.PROMPT + code
    system_prompt = prompts.SYS_PROMPT
    output = replicate.run(
        REPLICATE_EP,
        input={
            "debug": False,
            "top_p": 1,
            "prompt": prompt,
            "temperature": 0.5,
            "system_prompt": system_prompt,
            "max_new_tokens": 500,
            "min_new_tokens": -1,
            "prompt_template": "[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]",
            "repetition_penalty": 1.15,
        },
    )
    return "".join(output["output"])


def get_local_llm_output(code: str, language: str):
    """
    Get the local llm output.

    Parameters
    ----------
    code : str
        The code to be compiled.
    language : str
        The language to be compiled.

    Returns
    -------
    str
        The local llm output.
    """
    return inference.generate_docstring(code=code, language=language)
