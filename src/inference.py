import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from prompts import default_prompt
from logger import doctify_logger

torch.set_default_device("cuda")
torch.cuda.empty_cache()


class Inference:
    def __init__(self, model_name: str):
        self.model_name = model_name
        doctify_logger.info(f"Loading Tokenizer and Model for {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map={"": 0},
        )

    def post_process_text(self, output_text: str) -> str:
        return (
            output_text.split("<|separateoftext|>")[-1]
            .replace("<|endoftext|>", "")
            .strip()
        )

    def generate_docstring(
        self, code: str, language: str = "python", max_length: int = 400
    ) -> str:
        prompt = default_prompt.format(code=code)
        inputs = self.tokenizer(
            prompt, return_tensors="pt", return_attention_mask=False
        )

        outputs = self.model.generate(**inputs, max_length=max_length)

        return self.post_process_text(self.tokenizer.batch_decode(outputs)[0])


if __name__ == "__main__":
    model_name = "./models/phi2-phase2/checkpoint-600"

    code = """def __clean_code__(self, source_code : str, docstring : str) -> Tuple[str, str]:
        if not docstring:
            return None, None
        source_code = source_code.replace(docstring, "")
        docstring = docstring.replace('"', "")
        docstring = docstring.replace("'", "")
        return source_code, docstring #re.sub('\s+', ' ', source_code)"""

    inference = Inference(model_name)
    docstring = inference.generate_docstring(code, max_length=400)

    print(docstring)
