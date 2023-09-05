from pydantic import BaseModel
from .user import User  # Import the User model
from .transaction import Transaction  # Import the Transaction model
from uuid import UUID
from typing import List


class Account(BaseModel):
    account_number: str
    name: str
    user: UUID  # Use the User model as a type
