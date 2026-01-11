from datetime import date, timedelta
from decimal import Decimal

from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.payment import Payment
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus
from app.models.system_config import SystemConfig


def test_user_role_enum_and_repr():
    u = User(
        id=1,
        name="N",
        email="e@e.com",
        password_hash="x",
        role=UserRole.ADMIN.value,
        active=True,
        temporary_password=False,
    )
    assert u.role_enum == UserRole.ADMIN
    assert "User(" in repr(u) or "<User" in repr(u)


def test_customer_repr():
    c = Customer(
        id=1,
        full_name="A",
        cpf="000.000.000-00",
        phone="1",
        email=None,
        address=None,
        active=True,
    )
    assert "Customer" in repr(c)


def test_sale_repr():
    s = Sale(
        id=1,
        customer_id=1,
        user_id=1,
        description=None,
        total_amount=Decimal("10.00"),
        down_payment=Decimal("0.00"),
        installments_count=1,
        first_installment_date=date.today(),
    )
    assert "Sale" in repr(s)


def test_payment_total_amount_and_repr():
    p = Payment(
        id=1,
        promissory_note_id=1,
        amount_paid=Decimal("10.00"),
        payment_date=date.today(),
        interest_amount=Decimal("1.00"),
        fine_amount=Decimal("2.00"),
        notes=None,
    )
    assert p.total_amount == 13.0
    assert "Payment" in repr(p)


def test_promissory_note_properties_all_branches():
    today = date.today()

    n1 = PromissoryNote(
        id=1,
        sale_id=1,
        installment_number=1,
        original_amount=Decimal("100.00"),
        paid_amount=Decimal("20.00"),
        due_date=today - timedelta(days=10),
        payment_date=None,
        status=PromissoryNoteStatus.PENDING.value,
        notes=None,
    )
    assert n1.outstanding_balance == 80.0
    assert n1.days_overdue == 10
    assert n1.is_overdue is True
    assert "PromissoryNote" in repr(n1)

    n2 = PromissoryNote(
        id=2,
        sale_id=1,
        installment_number=1,
        original_amount=Decimal("50.00"),
        paid_amount=Decimal("50.00"),
        due_date=today - timedelta(days=10),
        payment_date=today,
        status=PromissoryNoteStatus.PAID.value,
        notes=None,
    )
    assert n2.days_overdue == 0
    assert n2.is_overdue is False

    n3 = PromissoryNote(
        id=3,
        sale_id=1,
        installment_number=1,
        original_amount=Decimal("10.00"),
        paid_amount=Decimal("0.00"),
        due_date=today + timedelta(days=5),
        payment_date=None,
        status=PromissoryNoteStatus.PENDING.value,
        notes=None,
    )
    assert n3.days_overdue == 0
    assert n3.is_overdue is False

    assert n1.status_enum == PromissoryNoteStatus.PENDING


def test_system_config_repr():
    sc = SystemConfig(
        id=1,
        company_name="X",
        logo_url=None,
        monthly_interest_rate=Decimal("1.00"),
        fine_rate=Decimal("2.00"),
        days_before_due_alert=5,
    )
    assert "SystemConfig" in repr(sc)
