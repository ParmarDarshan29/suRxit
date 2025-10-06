import os
import uuid
import shutil
from fastapi.testclient import TestClient
from services.ocr.main import app
from PIL import Image, ImageDraw

def create_sample_image(path):
    img = Image.new('RGB', (200, 60), color = (255,255,255))
    d = ImageDraw.Draw(img)
    d.text((10,10), "Paracetamol 500mg", fill=(0,0,0))
    img.save(path)

def test_ocr_upload():
    client = TestClient(app)
    sample_dir = 'data/uploads/test-sample/'
    os.makedirs(sample_dir, exist_ok=True)
    img_path = os.path.join(sample_dir, 'sample_rx.png')
    create_sample_image(img_path)
    with open(img_path, "rb") as f:
        response = client.post("/ocr/upload", files={"file": ("sample_rx.png", f, "image/png")})
    assert response.status_code == 200
    data = response.json()
    assert 'ingest_id' in data
    assert 'raw_text' in data and 'Paracetamol' in data['raw_text']
    assert 'blocks' in data and isinstance(data['blocks'], list)
    assert 'timestamp' in data
    # Cleanup
    shutil.rmtree(os.path.join('data/uploads', data['ingest_id']), ignore_errors=True)
    shutil.rmtree(sample_dir, ignore_errors=True)
