import csv
import io
from app.services.export_service import to_csv_bytes

def test_to_csv_bytes():
    headers = ["col1", "col2"]
    rows = [
        {"col1": "dado1", "col2": "dado2"},
        {"col1": "dado3", "col2": None} 
    ]
    
    csv_bytes = to_csv_bytes(headers=headers, rows=rows)
    
    content = csv_bytes.decode("utf-8")
    
    f = io.StringIO(content)
    reader = csv.DictReader(f)
    data = list(reader)
    
    assert len(data) == 2
    assert data[0]["col1"] == "dado1"
    assert data[1]["col2"] == "" 