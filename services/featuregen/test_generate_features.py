import pytest
from unittest.mock import MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_features

def test_compute_features_basic():
    # Mock prescription and neo4j session
    presc = ("rx1", "pat1", "d1,d2")
    mock_sess = MagicMock()
    # Mock DDI result (iterable)
    ddi_result = iter([
        {"severity": "high", "mechanism": "CYP"},
        {"severity": "moderate", "mechanism": "Pgp"}
    ])
    # Mock .single() return values for allergy, food, adr
    allergy_result = MagicMock()
    allergy_result.single.return_value = [2]
    food_result = MagicMock()
    food_result.single.return_value = [True]
    adr_result = MagicMock()
    adr_result.single.return_value = [3]
    # Set up side_effect for run
    mock_sess.run.side_effect = [ddi_result, allergy_result, food_result, adr_result]
    features = generate_features.compute_features(presc, mock_sess)
    assert features["prescription_id"] == "rx1"
    assert features["polypharmacy_count"] == 2
    assert features["high_severity_ddi_count"] == 1
    assert features["moderate_severity_ddi_count"] == 1
    assert set(features["unique_ddi_mechanisms"]) == {"CYP", "Pgp"}
    assert features["allergy_match_count"] == 2
    assert features["food_interaction_flag"] is True
    assert features["adr_count"] == 3
