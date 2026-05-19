from pydantic import BaseModel
from datetime import datetime


class ExpenseBase(BaseModel):
    amount: float
    category: str
    date: str
    description: str | None = None


class ExpenseCreate(ExpenseBase):
    user_id: int


class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True