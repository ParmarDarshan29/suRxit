# NER label mapping for clinical entities
LABELS = [
    "O",
    "B-DRUG", "I-DRUG",
    "B-DISEASE", "I-DISEASE",
    "B-ALLERGY", "I-ALLERGY",
    # Add more as needed
]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
ID2LABEL = {i: l for l, i in LABEL2ID.items()}
