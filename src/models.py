from datetime import date
from typing import Dict, List
from pydantic import BaseModel


class Asset(BaseModel):
    id: int
    name: str
    apr: float
    risk: int


class BaseStrategy(BaseModel):
    id: int
    date: date


class Strategy(BaseStrategy):
    allocation: Dict[int, float]


class Investment(BaseModel):
    id: int
    amount: float
    strategy_id: int
    date: date


class UserInvestmentMapping(BaseModel):
    id: int
    user_id: int
    investment_id: int


class User(BaseModel):
    id: int
    investments_ids: List[int]
