# suRxit Data Dictionary

## Node Files

### Common Properties
- **id**: Unique identifier for the node (string)
- **name**: Canonical name (string)
- **synonyms**: Alternative names, semicolon-separated (string)
- **codes**: External codes (see below)
- **severity**: Clinical severity (Low, Medium, High, N/A)
- **evidence_source**: Source of evidence (PubMed, Medline, etc.)
- **created_at**: Date of record creation (YYYY-MM-DD)

### Drug
- **DrugBank**: DrugBank ID (e.g., DB00945)
- **ATC**: Anatomical Therapeutic Chemical code (e.g., B01AC06)
- **ICD10_UMLS**: ICD-10 or UMLS code (e.g., N02BA01)

### SideEffect, Allergy, Food, Patient
- **ICD10_UMLS**: ICD-10 or UMLS code (if applicable)

## Relationship Files

### rels_ddi.csv (Drug-Drug Interaction)
- **start_id**: Source Drug id
- **end_id**: Target Drug id
- **severity**: Severity of interaction
- **mechanism**: Mechanism of interaction (e.g., CYP2C9 inhibition)
- **evidence**: Evidence source (PubMed, etc.)
- **confidence**: Confidence score (0-1)

### rels_adr.csv (Adverse Drug Reaction)
- **drug_id**: Drug id
- **sideeffect_id**: SideEffect id
- **severity**: Severity of reaction
- **evidence_source**: Evidence source
- **confidence**: Confidence score (0-1)

### rels_dfi.csv (Drug-Food Interaction)
- **drug_id**: Drug id
- **food_id**: Food id
- **severity**: Severity of interaction
- **mechanism**: Mechanism (e.g., inhibits metabolism)
- **evidence_source**: Evidence source
- **confidence**: Confidence score (0-1)

## Code Systems
- **DrugBank**: https://go.drugbank.com/
- **ATC**: https://www.whocc.no/atc_ddd_index/
- **ICD-10**: https://icd.who.int/browse10/2019/en
- **UMLS**: https://www.nlm.nih.gov/research/umls/

## Example
See each CSV for sample data and required columns.
