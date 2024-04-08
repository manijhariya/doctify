# Imports
import os
from pathlib import Path

import jsonlines
import pandas as pd
import torch
from datasets import load_dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          BitsAndBytesConfig, HfArgumentParser,
                          TrainingArguments)
from trl import SFTTrainer

from src.logger import doctify_logger

torch.cuda.empty_cache()


def format_row(row: Dict[str, str]) -> str:
    return f'<|beginoftext|> {row["code"]} <|separateoftext|> {row["docstring"]} <|endoftext|>'


def load_all_data_files(file_path: Path) -> pd.DataFrame:
    data = []
    for file in os.listdir(file_path):
        with jsonlines.open(f"{file_path}/{file}", "r") as reader:
            data.extend(list(reader))
    return data


def build_training_data(processed_data: Path, output_dir: Path) -> None:
    dataset = load_all_data_files(processed_data)
    df = pd.DataFrame(dataset)
    df["Text"] = df.apply(format_row, axis=1)
    new_df = df[["Text"]]

    os.makedirs(output_dir, exist_ok=True)

    new_df.to_csv(output_dir / "formatted_data.csv", index=False)


def load_training_dataset(data_file_path: Path):
    return load_dataset("csv", data_files=data_file_path, split="train")


def build_and_load_tokenizer(model_name: str) -> AutoTokenizer:
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
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
    return tokenizer


def build_and_load_training_model(model_name: str) -> SFTTrainer:
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=False,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        # attn_implementation="flash_attention_2",
        low_cpu_mem_usage=True,
        device_map={"": 0},
    )

    model.config.use_cache = False
    model.config.pretraining_tp = 1

    return prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)


def build_and_load_trainer(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    training_dataset: dataset,
    *args,
    **kwargs,
) -> SFTTrainer:
    training_arguments = TrainingArguments(
        output_dir=kwargs.get("output_dir", "./models/phi2/"),
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

    return trainer


def finetune(model_name: str) -> None:
    processed_file_path = Path("./data/processed")
    output_file_path = Path("./data/output")
    build_training_data(processed_file_path, output_file_path)

    training_dateset_path = Path("./data/output/formatted_data.csv")
    training_dataset = load_training_dataset(training_dateset_path)

    tokenizer = build_and_load_tokenizer(mode_name)

    model = build_and_load_training_model(model_name)

    trainer = build_and_load_trainer(model, tokenizer, training_dataset)

    trainer.train()

    trainer.model.save()


if __name__ == "__main__":
    base_model = "./models/phi2/checkpoint-250"
    finetune(base_model)
