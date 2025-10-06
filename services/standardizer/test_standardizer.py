from fastapi.testclient import TestClient
from services.standardizer.main import app

def test_standardize_entities():
    client = TestClient(app)
    # Simulate a drug entity that should match nodes_drug.csv
    entities = [
        {"text": "Paracetamol", "type": "DRUG"},
        {"text": "UnknownDrug", "type": "DRUG"}
    ]
    response = client.post("/standardize", json={"entities": entities})
    assert response.status_code == 200
    data = response.json()
    assert 'results' in data
    assert isinstance(data['results'], list)
    # At least one result should have a canonical_id or manual_review_flag
    found_match = any(r['canonical_id'] and not r['manual_review_flag'] for r in data['results'])
    found_flag = any(r['manual_review_flag'] for r in data['results'])
    assert found_match or found_flag
