from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.payment import Payment
from app.models.promissory_note import PromissoryNote
from app.models.sale import Sale
from app.models.system_config import SystemConfig


def _money(value: Any) -> str:
    # Decimal / numeric -> string padronizada
    try:
        return f"{value:.2f}"
    except Exception:
        return str(value)


def build_payment_receipt_pdf(db: Session, *, payment_id: int) -> bytes | None:
    """
    RF11 - Gerar recibo em PDF para um pagamento já registrado.
    Retorna bytes do PDF ou None se não encontrar.
    """

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return None

    note = (
        db.query(PromissoryNote)
        .filter(PromissoryNote.id == payment.promissory_note_id)
        .first()
    )
    if not note:
        return None

    sale = db.query(Sale).filter(Sale.id == note.sale_id).first()
    if not sale:
        return None

    customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
    if not customer:
        return None

    # Pega config (se não existir, cai num default simples sem quebrar)
    cfg = db.query(SystemConfig).order_by(SystemConfig.id.asc()).first()
    company_name = cfg.company_name if cfg else "Minha Empresa"

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Layout simples e consistente
    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "RECIBO DE PAGAMENTO")
    y -= 24

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Empresa: {company_name}")
    y -= 18

    c.drawString(50, y, f"Cliente: {customer.full_name}")
    y -= 18

    c.drawString(50, y, f"CPF: {customer.cpf}")
    y -= 18

    c.drawString(50, y, f"Telefone: {customer.phone}")
    y -= 18

    if customer.email:
        c.drawString(50, y, f"E-mail: {customer.email}")
        y -= 18

    if customer.address:
        c.drawString(50, y, f"Endereço: {customer.address}")
        y -= 18

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Dados do Pagamento")
    y -= 18
    c.setFont("Helvetica", 11)

    c.drawString(50, y, f"Pagamento ID: {payment.id}")
    y -= 16

    c.drawString(50, y, f"Promissória ID: {note.id}")
    y -= 16

    c.drawString(50, y, f"Venda ID: {sale.id}")
    y -= 16

    c.drawString(50, y, f"Parcela: {note.installment_number}")
    y -= 16

    c.drawString(50, y, f"Data do pagamento: {payment.payment_date.isoformat()}")
    y -= 16

    c.drawString(50, y, f"Vencimento da parcela: {note.due_date.isoformat()}")
    y -= 16

    y -= 6
    c.drawString(50, y, f"Valor pago: R$ {_money(payment.amount_paid)}")
    y -= 16
    c.drawString(50, y, f"Juros: R$ {_money(payment.interest_amount)}")
    y -= 16
    c.drawString(50, y, f"Multa: R$ {_money(payment.fine_amount)}")
    y -= 16

    total = payment.total_amount
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, f"Total: R$ {_money(total)}")
    y -= 22

    c.setFont("Helvetica", 10)
    c.drawString(
        50,
        y,
        "Declaro ter recebido do cliente acima identificado o valor descrito neste recibo.",
    )
    y -= 40

    c.drawString(50, y, "Assinatura: _________________________________")
    y -= 18

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 40, "Documento gerado automaticamente pelo CrediGestor.")

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
