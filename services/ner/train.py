"""
Train a Clinical NER model (BioBERT) on IOB-annotated data in data/annotated/.
Usage:
    python train.py --epochs 5 --batch_size 16 --lr 3e-5 --output_dir ./model
"""
import argparse
import os
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, Trainer, TrainingArguments
from datasets import Dataset, DatasetDict
try:
    from datasets import load_metric
except ImportError:
    from evaluate import load as load_metric
from labels import LABELS, LABEL2ID
import pandas as pd

def read_iob_csv(path):
    # Reads a CSV with columns: token,label (empty line = new sentence)
    sentences, labels = [], []
    cur_sent, cur_labels = [], []
    with open(path, 'r') as f:
        next(f)  # skip header
        for line in f:
            line = line.strip()
            if not line:
                if cur_sent:
                    sentences.append(cur_sent)
                    labels.append(cur_labels)
                    cur_sent, cur_labels = [], []
                continue
            token, label = line.split(',')
            cur_sent.append(token)
            cur_labels.append(label)
        if cur_sent:
            sentences.append(cur_sent)
            labels.append(cur_labels)
    return sentences, labels

def load_iob_data(data_dir):
    train_sents, train_labels = read_iob_csv(os.path.join(data_dir, 'train.csv'))
    valid_sents, valid_labels = read_iob_csv(os.path.join(data_dir, 'valid.csv'))
    train_data = {"tokens": train_sents, "labels": [[LABEL2ID[l] for l in seq] for seq in train_labels]}
    valid_data = {"tokens": valid_sents, "labels": [[LABEL2ID[l] for l in seq] for seq in valid_labels]}
    return DatasetDict({
        "train": Dataset.from_dict(train_data),
        "validation": Dataset.from_dict(valid_data)
    })

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=3e-5)
    parser.add_argument('--output_dir', type=str, default='./model')
    args = parser.parse_args()

    model_name = 'dmis-lab/biobert-base-cased-v1.1'
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForTokenClassification.from_pretrained(
        model_name, num_labels=len(LABELS), id2label={str(i): l for i, l in enumerate(LABELS)}, label2id={l: i for i, l in enumerate(LABELS)}
    )

    dataset = load_iob_data('data/annotated')

    def tokenize_and_align_labels(examples):
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
                    # For subwords, assign -100 so they're ignored in loss
                    label_ids.append(-100)
                prev_word_idx = word_idx
            labels.append(label_ids)
        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    tokenized_datasets = dataset.map(tokenize_and_align_labels, batched=True)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.lr,
        logging_dir=os.path.join(args.output_dir, "logs"),
        logging_steps=10,
    )

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
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(args.output_dir)

if __name__ == '__main__':
    main()
