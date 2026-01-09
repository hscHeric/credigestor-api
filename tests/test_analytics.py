import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app
from app.models.user import User
from app.router.auth_routes import get_current_user

# test de integração 4 - rotas Relatórios / Dashboard

@pytest.fixture(autouse=True)
def mock_login():
    def mock_get_current_user():
        return User(id=1, email="admin@teste.com", role="admin", active=True)
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield


def test_dashboard_metrics(client: TestClient):
    """
    Testa se o Dashboard carrega e calcula os totais corretamente.
    """
    cust = client.post("/api/customers", json={"full_name":"Cliente Dash", "cpf":"888.888.888-88", "phone":"11"})
    cust_id = cust.json()["id"]

    sale_data = {
        "customer_id": cust_id,
        "total_amount": 1000.00,
        "down_payment": 100.00,
        "installments_count": 5,
        "first_installment_date": str(date.today()),
        "description": "Venda para Dashboard"
    }
    client.post("/api/sales", json=sale_data)

    response = client.get("/api/dashboard")
    
    assert response.status_code == 200
    data = response.json()

    # Verifica os campos reais que o sistema devolve (baseado no log de erro)
    assert "total_to_receive" in data
    assert "received_last_30_days" in data
    assert "total_overdue" in data
    

    assert float(data["total_to_receive"]) >= 900.00

def test_delinquency_report(client: TestClient):
    """
    Testa se a rota de Relatório de Inadimplência responde com a estrutura certa.
    """
    response = client.get("/api/reports/delinquency")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, dict)
    
    # Verifica se dentro do dicionário tem a lista de clientes e os totais
    assert "customers" in data
    assert isinstance(data["customers"], list)
    assert "total_due_all" in data