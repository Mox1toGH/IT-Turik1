from datetime import datetime
from typing import Literal

from ninja import Field, Schema
from pydantic import model_validator

class PointsBalanceResponse(Schema):
    user_id: int
    balance: int
    updated_at: datetime


class PointsTransactionResponse(Schema):
    id: int
    user_id: int
    order_id: int | None = None
    amount: int
    reason: str
    created_at: datetime


class ModifyPointsRequest(Schema):
    operation: Literal['add', 'subtract', 'set', 'reset']
    amount: int | None = None
    reason: str = Field(..., max_length=255)

    @model_validator(mode='after')
    def validate_amount(self):
        if self.operation in {'add', 'subtract', 'set'} and self.amount is None:
            raise ValueError('amount is required for this operation.')
        if self.operation == 'reset' and self.amount is not None:
            raise ValueError('amount must not be provided for reset.')
        if self.operation in {'add', 'subtract'} and self.amount is not None and self.amount < 0:
            raise ValueError('Use a non-negative amount for add/subtract operations.')
        return self


class UserLookupResponse(Schema):
    id: int
    username: str
    email: str


class ModifyPointsResponse(Schema):
    user: UserLookupResponse
    balance: PointsBalanceResponse
    transaction: PointsTransactionResponse
