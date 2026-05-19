from pydantic import BaseModel


CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


class Category(BaseModel):
    name: str


def get_categories():
    return CATEGORIES