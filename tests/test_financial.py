import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app
from app.models.user import User
from app.router.auth_routes import get_current_user

# Teste de integração 3 - lógica Financeira

@pytest.fixture(autouse=True)
def mock_login():
    def mock_get_current_user():
        return User(id=1, email="admin@teste.com", role="admin", active=True)
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield

def test_financial_cycle(client: TestClient):
    """
    Testa o ciclo completo:
    Venda -> Ver Notas -> Pagar Nota -> Verificar Baixa
    """
    
    cust = client.post("/api/customers", json={"full_name":"Devedor", "cpf":"999.999.999-99", "phone":"11"})
    customer_id = cust.json()["id"]

    sale_data = {
        "customer_id": customer_id,
        "total_amount": 100.00,
        "down_payment": 0.00,
        "installments_count": 2, 
        "first_installment_date": str(date.today()),
        "description": "Ciclo Financeiro"
    }
    sale_res = client.post("/api/sales", json=sale_data)
    assert sale_res.status_code == 201
    
    note_id = sale_res.json()["promissory_notes"][0]["id"]

    #  Pomissórias: Listar
    list_res = client.get("/api/promissory-notes") 
    assert list_res.status_code == 200
    notes = list_res.json()
    assert len(notes) >= 2
    
    my_note = next(n for n in notes if n["id"] == note_id)
    assert my_note["status"] == "pending"

    # 3. pagamento: Pagar a Nota
    payment_data = {
        "amount_paid": 50.00,
        "payment_date": str(date.today()),
        "interest_amount": 0,
        "fine_amount": 0
    }
    
    pay_res = client.post(f"/api/promissory-notes/{note_id}/payments", json=payment_data)
    
    assert pay_res.status_code == 201
    
    note_res = client.get(f"/api/promissory-notes/{note_id}")
    assert note_res.status_code == 200
    updated_note = note_res.json()
    
    assert updated_note["status"] == "paid"
    assert float(updated_note["paid_amount"]) == 50.00