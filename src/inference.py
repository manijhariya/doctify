import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.logger import doctify_logger
from src.prompts import default_prompt

torch.set_default_device("cuda")
torch.cuda.empty_cache()


class Inference:
    def __init__(self, model_name: str):
        """
        Initialize the model.

        Parameters
        ----------
        model_name : str
            The name of the model to load.
        """
        self.model_name = model_name
        doctify_logger.info(f"Loading Tokenizer and Model for {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map={"": 0},
        )

    def post_process_text(self, output_text: str) -> str:
        """
        Post process the text output from the model.

        Parameters
        ----------
        output_text : str
            The text output from the model.

        Returns
        -------
        str
            The post processed text output.
        """
        return (
            output_text.split("<|separateoftext|>")[-1]
            .replace("<|endoftext|>", "")
            .strip()
        )

    def generate_docstring(
        self, code: str, language: str = "python", max_new_tokens: int = 400
    ) -> str:
        """
        Generate a docstring from a code snippet.

        Parameters
        ----------
        code : str
            The code snippet to generate a docstring from.
        language : str, default=python
            The language to generate the docstring in.
        max_length : int, default=400
            The maximum length of the generated docstring.

        Returns
        -------
        docstring : str
            The generated docstring.

        Examples
        --------
        >>> from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        >>> tokenizer = AutoTokenizer.from_pretrained("t5-base")
        >>> model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
        >>> docstring = model.generate_docstring(code=f"def foo(x): return x + 1")
        >>> docstring
        >>> def foo(x):
        >>>    return x + 1
        >>>
        """
        prompt = default_prompt.format(code=code)
        inputs = self.tokenizer(
            prompt, return_tensors="pt", return_attention_mask=False
        )

        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)

        return self.post_process_text(self.tokenizer.batch_decode(outputs)[0])

    def close_llm(self):
        """
        Close the model and tokenizer.

        This is called automatically when the object is deleted.
        """
        del self.model
        del self.tokenizer

        torch.cuda.empty_cache()


if __name__ == "__main__":
    model_name = "manijhriya/phi2-doctify"

    code = """def __clean_code__(self, source_code : str, docstring : str) -> Tuple[str, str]:
        if not docstring:
            return None, None
        source_code = source_code.replace(docstring, "")
        docstring = docstring.replace('"', "")
        docstring = docstring.replace("'", "")
        return source_code, docstring #re.sub('\s+', ' ', source_code)"""

    inference = Inference(model_name)
    docstring = inference.generate_docstring(code, max_new_tokens=400)


    print(docstring)
