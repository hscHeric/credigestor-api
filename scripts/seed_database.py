import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Customer, User, SystemConfig, PromissoryNote
from app.services.sale_service import create_sale_and_promissory_notes
from app.services.payment_service import register_payment
from app.schemas.sale_schema import SaleCreate
from app.schemas.payment_schema import PaymentCreate


def seed_db_massive(db: Session):
    # 1. Configuração do Sistema (CHOAM)
    config = db.query(SystemConfig).first()
    if not config:
        config = SystemConfig(
            company_name="CHOAM - Arrakis Division",
            monthly_interest_rate=Decimal("3.00"),
            fine_rate=Decimal("10.00"),
        )
        db.add(config)

    user = db.query(User).filter(User.email == "admin@credigestor.com").first()
    if not user:
        return {"error": "Execute o script create_admin.py primeiro."}

    # 2. Gerar Clientes Randômicos (Nomes de Duna)
    first_names = [
        "Paul",
        "Leto",
        "Duncan",
        "Gurney",
        "Baron",
        "Piter",
        "Feyd",
        "Stilgar",
        "Chani",
        "Liet",
    ]
    last_names = [
        "Atreides",
        "Harkonnen",
        "Idaho",
        "Halleck",
        "Kynes",
        "de Vries",
        "Rautha",
    ]

    for i in range(50):  # 50 clientes iniciais
        cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)} {i}"
        if not db.query(Customer).filter(Customer.cpf == cpf).first():
            cust = Customer(
                full_name=name,
                cpf=cpf,
                phone=f"60-9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                email=f"user{i}@arrakis.com",
            )
            db.add(cust)
    db.commit()

    # 3. Gerar Vendas Massivas (Centenas de Promissórias)
    customers = db.query(Customer).all()
    today = date.today()

    for _ in range(100):  # 100 vendas
        cust = random.choice(customers)
        total = Decimal(random.uniform(1000, 20000)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        down = Decimal(total * Decimal(random.uniform(0, 0.2))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        sale_data = SaleCreate(
            customer_id=cust.id,
            description=random.choice(
                [
                    "Lote de Melange",
                    "Equipamento Destilador",
                    "Ornitóptero usado",
                    "Água da vida",
                ]
            ),
            total_amount=total,
            down_payment=down,
            installments_count=random.randint(1, 12),
            first_installment_date=today - timedelta(days=random.randint(0, 180)),
        )
        # O serviço já cria as PromissoryNotes automaticamente
        create_sale_and_promissory_notes(db, user_id=user.id, data=sale_data)

    # 4. Lógica Probabilística de Pagamentos via Service
    all_notes = db.query(PromissoryNote).all()

    for note in all_notes:
        r = random.random()

        # 55% - Pagamento Integral
        if r < 0.55:
            payment_date = note.due_date - timedelta(days=random.randint(-5, 5))
            if payment_date > today:
                payment_date = today

            pay_data = PaymentCreate(
                amount_paid=note.original_amount,
                payment_date=payment_date,
                notes="Pagamento integral (a especiaria deve fluir)",
            )
            try:
                register_payment(db, promissory_note_id=note.id, data=pay_data)
            except:
                db.rollback()

        # 20% - Pagamento Parcial (1 ou 2 vezes)
        elif r < 0.75:
            percent = Decimal(random.uniform(0.3, 0.8))
            val1 = (note.original_amount * percent).quantize(Decimal("0.01"))

            pay_data = PaymentCreate(
                amount_paid=val1,
                payment_date=note.due_date,
                notes="Pagamento parcial (o deserto é implacável)",
            )
            try:
                register_payment(db, promissory_note_id=note.id, data=pay_data)

                # Chance de uma segunda parte do parcial
                if random.random() < 0.5:
                    val2 = (note.original_amount - val1) * Decimal(0.5)
                    pay_data2 = PaymentCreate(
                        amount_paid=val2.quantize(Decimal("0.01")),
                        payment_date=note.due_date + timedelta(days=2),
                        notes="Segunda parte do parcial",
                    )
                    register_payment(db, promissory_note_id=note.id, data=pay_data2)
            except:
                db.rollback()

        # 25% - Inadimplente (não faz nada, fica overdue se a data passou)

    db.commit()
    return {"total_notes": len(all_notes)}

