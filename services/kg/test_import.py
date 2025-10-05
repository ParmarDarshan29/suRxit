import pytest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("kg_import", os.path.join(os.path.dirname(__file__), "import.py"))
kg_import = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kg_import)

def test_import_nodes_runs():
    # Prepare a fake transaction and CSV
    tx = MagicMock()
    label = "Drug"
    # Create a temporary CSV file
    import tempfile, csv
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='') as tmp:
        writer = csv.DictWriter(tmp, fieldnames=['id', 'name'])
        writer.writeheader()
        writer.writerow({'id': 'd1', 'name': 'Aspirin'})
        tmp_path = tmp.name
    kg_import.import_nodes(tx, label, tmp_path)
    tx.run.assert_called()
    os.remove(tmp_path)

def test_import_rels_runs():
    tx = MagicMock()
    rel_type = "HAS_ADR"
    import tempfile, csv
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='') as tmp:
        writer = csv.DictWriter(tmp, fieldnames=['drug_id', 'sideeffect_id', 'note'])
        writer.writeheader()
        writer.writerow({'drug_id': 'd1', 'sideeffect_id': 's1', 'note': 'test'})
        tmp_path = tmp.name
    kg_import.import_rels(tx, rel_type, tmp_path)
    tx.run.assert_called()
    os.remove(tmp_path)
