
# NER Service

## Overview
This service provides a Named Entity Recognition (NER) API for extracting clinical entities from text using BioBERT.

## Training
Fine-tune BioBERT on IOB-annotated data in `data/annotated/`.

### Train
```bash
python train.py --epochs 5 --batch_size 16 --lr 3e-5 --output_dir ./model
```

### Evaluate
Outputs Precision, Recall, F1 on validation set.
```bash
python eval.py --model_dir ./model
```

**Acceptance:** F1 ≥ defined threshold on validation set.

## Endpoints
- `POST /ner/parse`: Extracts clinical entities (DRUG, DOSAGE, FREQ, DISEASE, ALLERGY) from text.

## Environment Variables
- `MODEL_NAME` (optional): HuggingFace model name (default: dmis-lab/biobert-base-cased-v1.1)

## Running Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Testing
```bash
pytest test_ner.py
```
