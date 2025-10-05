"""
Evaluate a trained NER model on validation set. Outputs Precision, Recall, F1.
Usage:
    python eval.py --model_dir ./model
"""

import os
import argparse
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, Trainer
from datasets import Dataset, DatasetDict
try:
    from datasets import load_metric
except ImportError:
    from evaluate import load as load_metric
from labels import LABELS, LABEL2ID
import pandas as pd
from train import read_iob_csv

def load_validation_dataset(data_dir):
    valid_sents, valid_labels = read_iob_csv(os.path.join(data_dir, 'valid.csv'))
    valid_data = {"tokens": valid_sents, "labels": [[LABEL2ID[l] for l in seq] for seq in valid_labels]}
    return Dataset.from_dict(valid_data)

def tokenize_and_align_labels(examples, tokenizer):
    tokenized_inputs = tokenizer(
        examples["tokens"], truncation=True, is_split_into_words=True, padding=True
    )
    labels = []
    for i, label in enumerate(examples["labels"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = []
        prev_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != prev_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append(-100)
            prev_word_idx = word_idx
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_dir', type=str, required=True)
    parser.add_argument('--data_dir', type=str, default='data/annotated')
    args = parser.parse_args()

    model = AutoModelForTokenClassification.from_pretrained(args.model_dir)
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)

    valid_dataset = load_validation_dataset(args.data_dir)
    tokenized_valid = valid_dataset.map(lambda x: tokenize_and_align_labels(x, tokenizer), batched=True)

    metric = load_metric("seqeval")

    def compute_metrics(p):
        predictions, labels = p
        predictions = predictions.argmax(-1)
        true_labels = [[LABELS[l] for l in label if l != -100] for label in labels]
        true_preds = [
            [LABELS[pred] for (pred, lab) in zip(prediction, label) if lab != -100]
            for prediction, label in zip(predictions, labels)
        ]
        results = metric.compute(predictions=true_preds, references=true_labels)
        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"],
        }

    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
    )
    outputs = trainer.predict(tokenized_valid)
    metrics = compute_metrics((outputs.predictions, outputs.label_ids))
    print("Evaluation Results:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

if __name__ == '__main__':
    main()
