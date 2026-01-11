import io
import zipfile
from unittest.mock import MagicMock, patch
from app.services.backup_service import _list_tables, _copy_table_csv, build_backup_zip

def test_list_tables():
    mock_engine = MagicMock()
    mock_conn = mock_engine.connect.return_value.__enter__.return_value
    mock_conn.execute.return_value.fetchall.return_value = [("users",), ("sales",)]
    
    tables = _list_tables(mock_engine)
    assert tables == ["users", "sales"]

def test_copy_table_csv_psycopg2():
    """Testa o caminho principal: driver com copy_expert (psycopg2)"""
    mock_engine = MagicMock()
    mock_raw = mock_engine.raw_connection.return_value.__enter__.return_value
    mock_cursor = mock_raw.cursor.return_value
    
    def side_effect(sql, buf):
        buf.write("id,name\n1,psycopg2")
    
    mock_cursor.copy_expert.side_effect = side_effect
    
    result = _copy_table_csv(mock_engine, "users")
    assert result == b"id,name\n1,psycopg2"
    mock_cursor.copy_expert.assert_called()

def test_copy_table_csv_fallback():
    """Testa o caminho de fallback (psycopg3) """
    mock_engine = MagicMock()
    mock_raw = mock_engine.raw_connection.return_value.__enter__.return_value
    mock_cursor = mock_raw.cursor.return_value
    
    del mock_cursor.copy_expert
    
    mock_copy_result = MagicMock()
    mock_copy_result.rows.return_value = ["id,val\n", "10,fallback\n"]
    mock_cursor.copy.return_value = mock_copy_result
    
    result = _copy_table_csv(mock_engine, "test_table")
    
    assert result == b"id,val\n10,fallback\n"
    
    mock_cursor.copy.assert_called()

@patch("app.services.backup_service._list_tables")
@patch("app.services.backup_service._copy_table_csv")
def test_build_backup_zip(mock_copy, mock_list):
    mock_engine = MagicMock()
    mock_list.return_value = ["users"]
    mock_copy.return_value = b"id,name\n1,teste"
    
    filename, zip_bytes = build_backup_zip(mock_engine)
    
    assert filename.startswith("credigestor_backup_")
    assert filename.endswith(".zip")
    assert len(zip_bytes) > 0
    
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        lista_arquivos = zf.namelist()
        assert "manifest.json" in lista_arquivos
        assert "data/users.csv" in lista_arquivos