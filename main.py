import os
import json
from flask import Flask, request, jsonify
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
from torch.utils.data import Dataset

# Step 1: Define a custom Dataset
class VueDataset(Dataset):
    def __init__(self, dataset_file, tokenizer):
        with open(dataset_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.samples = [item["source_code"] for item in data]
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        encoding = self.tokenizer(sample, truncation=True, padding="max_length", max_length=512)
        encoding["labels"] = encoding["input_ids"].copy()
        return encoding

# Step 2: Fine-tune GPT-2
def train_gpt2(dataset_path, output_dir):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token  # Set the padding token
    model = GPT2LMHeadModel.from_pretrained("gpt2")

    # Load dataset
    dataset = VueDataset(dataset_path, tokenizer)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=5,
        per_device_train_batch_size=10,
        save_steps=10_000,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

# Step 3: Build Flask API
def create_flask_api(model_dir):
    app = Flask(__name__)

    # Load trained model and tokenizer
    model = GPT2LMHeadModel.from_pretrained(model_dir)
    tokenizer = GPT2Tokenizer.from_pretrained(model_dir)
    tokenizer.pad_token = tokenizer.eos_token  # Set the padding token

    @app.route("/generate", methods=["POST"])
    def generate():
        # Get prompt from user
        data = request.json
        prompt = data.get("prompt", "")

        # Generate text
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        outputs = model.generate(inputs, max_length=150, num_return_sequences=1)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return jsonify({"output": result})

    return app

# Main workflow
if __name__ == "__main__":
    # Paths
    dataset_file = "./vue_dataset.json"
    model_output_dir = "./trained_gpt2"

    # Step 1: Train the model
    train_gpt2(dataset_file, model_output_dir)

    # Step 2: Run the Flask API
    api = create_flask_api(model_output_dir)
    api.run(host="0.0.0.0", port=5000)