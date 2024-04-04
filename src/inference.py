# %%
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

torch.set_default_device("cuda")
torch.cuda.empty_cache()


model_path = "./models/phi2/checkpoint-100"
# model_path = "microsoft/phi-2"

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map={"": 0},
)
tokenizer = AutoTokenizer.from_pretrained(model_path)
# tokenizer.pad_token_id = tokenizer.eos_token_id
# tokenizer.padding_side = "right"
# %%
# in_text = "I have sucidial thoughts what should we do?"

in_text = """<|beginoftext|>def get_crypto_input(self, kt_element: NamedTuple) -> AbstractCryptoInput:
    return CryptoInput(kt_element=kt_element)<|separateoftext|>"""

code = """def __clean_code__(self, source_code : str, docstring : str) -> Tuple[str, str]:
    if not docstring:
        return None, None
    source_code = source_code.replace(docstring, "")
    docstring = docstring.replace('"', "")
    docstring = docstring.replace("'", "")
    return source_code, docstring #re.sub('\s+', ' ', source_code)"""


in_text = f"<|beginoftext|>{code}<|separateoftext|>"
inputs = tokenizer(in_text, return_tensors="pt", return_attention_mask=False)

outputs = model.generate(
    **inputs,
    max_length=200,
)
text = tokenizer.batch_decode(outputs)[0]
print(text)
