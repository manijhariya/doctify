# %%
# Imports
import os

import jsonlines
import pandas as pd
import torch
from datasets import load_dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          BitsAndBytesConfig, HfArgumentParser,
                          TrainingArguments)
from trl import SFTTrainer

torch.cuda.empty_cache()


# %%
def load_all_data_files(file_path):
    data = []
    for file in os.listdir(file_path):
        with jsonlines.open(f"{file_path}/{file}", "r") as reader:
            data.extend(list(reader))
    return data


dataset = load_all_data_files("./data/processed")

# Load and Preprocess dataset
df = pd.DataFrame(dataset)


# %%
def format_row(row):
    return f'<|beginoftext|> {row["code"]} <|separateoftext|> {row["docstring"]} <|endoftext|>'


df["Text"] = df.apply(format_row, axis=1)
# %%
new_df = df[["Text"]]
new_df.head()

os.makedirs("./data/output", exist_ok=True)

new_df.to_csv("./data/output/formatted_data.csv", index=False)
# %%
# Save Training Data
training_dataset = load_dataset(
    "csv", data_files="./data/output/formatted_data.csv", split="train"
)

# %%
# Fine Tuning Code
base_model = "microsoft/phi-2"
new_model = "phi2-code-docstring"


tokenizer = AutoTokenizer.from_pretrained(
    base_model,
    use_fast=True,
    add_eos_token=True,
)
tokenizer.add_special_tokens(
    {
        "bos_token": "<|beginoftext|>",
        "eos_token": "<|endoftext|>",
        "pad_token": "<|padoftext|>",
        "sep_token": "<|separateoftext|>",
    }
)
tokenizer.padding_side = "right"
# %%
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=False,
)

# %%
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_config,
    # attn_implementation="flash_attention_2",
    low_cpu_mem_usage=True,
    device_map={"": 0},
)

model.config.use_cache = False
model.config.pretraining_tp = 1

model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

# %%
training_arguments = TrainingArguments(
    output_dir="./models/phi2/",
    num_train_epochs=10,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    evaluation_strategy="steps",
    eval_steps=1000,
    logging_steps=15,
    optim="paged_adamw_8bit",
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    save_steps=50,
    warmup_ratio=0.05,
    weight_decay=0.01,
    max_steps=-1,
)

peft_config = LoraConfig(
    r=32,
    lora_alpha=64,
    lora_dropout=0.05,
    bias="none",
    task_type="CASUAL_LM",
    target_modules=["Wqkv", "fc1", "fc2"],
)

trainer = SFTTrainer(
    model=model,
    train_dataset=training_dataset,
    peft_config=peft_config,
    dataset_text_field="Text",
    max_seq_length=690,
    tokenizer=tokenizer,
    args=training_arguments,
)
# %%
trainer.train()
