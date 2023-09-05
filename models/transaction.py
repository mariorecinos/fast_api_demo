from pydantic import BaseModel
from datetime import date
from uuid import UUID

class Transaction(BaseModel):
    id: str | None = None
    title: str
    type: str
    amount: float
    date: date
    user_id: UUID  # ID of the user who added the transaction
    account_number: str  # Account number to which the transaction belongs
