from datetime import date
from typing import Dict, List
from pydantic import BaseModel, validator


class Message(BaseModel):
    message: str


class AssetIn(BaseModel):
    name: str
    apr: float
    risk: int

    @validator("apr")
    def apr_must_be_in_range(cls, v):
        if v < 0 or v > 1:
            raise ValueError("The APR must be between 0 and 1, as it is a percentage")
        return v

    @validator("risk")
    def risk_must_be_in_range(cls, v):
        if v < 1 or v > 6:
            raise ValueError("The risk must be between 1 and 6")
        return v


class Asset(AssetIn):
    id: int


class BaseStrategy(BaseModel):
    id: int
    date: date


class StrategyIn(BaseModel):
    date: date
    allocation: Dict[int, float]

    @validator("allocation")
    def allocation_must_sum_up_to_1(cls, v):
        total = sum(v.values())
        if total < 0 or total > 1:
            raise ValueError(
                "The total allocation must be between 0 and 1, as it is a percentage"
            )
        return v


class Strategy(BaseStrategy):
    allocation: Dict[int, float]

    @validator("allocation")
    def allocation_must_sum_up_to_1(cls, v):
        total = sum(v.values())
        if total < 0 or total > 1:
            raise ValueError(
                "The total allocation must be between 0 and 1, as it is a percentage"
            )
        return v


class InvestmentIn(BaseModel):
    amount: float
    strategy_id: int
    date: date

    @validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("The amount must be positive")
        return v


class Investment(InvestmentIn):
    id: int


class UserInvestmentMapping(BaseModel):
    id: int
    user_id: int
    investment_id: int


class User(BaseModel):
    id: int
    investments_ids: List[int]
