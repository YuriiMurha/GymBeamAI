import json
import transformers
from transformers import LlamaForCausalLM, LlamaTokenizer, Trainer, TrainingArguments
from datasets import load_dataset

# Load data
file_path = 'processed_data.jsonl'
articles = []

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        article = json.loads(line)
        articles.append({
            "author": article["metadata"]["author"],
            "text": article["text"],
            "date": article["metadata"]["creation_date"],
            "keywords": article["metadata"]["keywords"]
        })

# Initialize tokenizer and model
tokenizer = LlamaTokenizer.from_pretrained("path/to/llama-model")
model = LlamaForCausalLM.from_pretrained("path/to/llama-model")

# Tokenize data
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)

# Convert to dataset format
dataset = load_dataset('json', data_files=file_path, split='train')
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    weight_decay=0.01,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    logging_dir="./logs",
)

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# Train the model
trainer.train()

# Save the model
model.save_pretrained("./trained_llama_model")
tokenizer.save_pretrained("./trained_llama_model")