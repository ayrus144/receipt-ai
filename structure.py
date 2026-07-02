from pydantic import BaseModel


class Field(BaseModel):
    value: str | float | None = None
    confidence: float = 0.0


class Receipt(BaseModel):
    company: Field
    invoice_number: Field
    date: Field
    total: Field