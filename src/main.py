import pyfuncol
from typing import List
import databases
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from . import crud
from .models import (
    Asset,
    BaseStrategy,
    Investment,
    Strategy,
    User,
    UserInvestmentMapping,
)
from .config import DATABASE_URL


database = databases.Database(DATABASE_URL)

app = FastAPI(title="Investment planner")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/assets", response_model=List[Asset], status_code=status.HTTP_200_OK)
async def get_assets(skip: int = 0, take: int = 50):
    assets = await crud.get_assets(database, skip, take)
    return [Asset.parse_obj(asset) for asset in assets]


@app.get("/assets/{id}", response_model=Asset, status_code=status.HTTP_200_OK)
async def get_asset(id: int):
    asset = await crud.get_asset(database, id)
    return Asset.parse_obj(asset)


@app.get(
    "/strategies", response_model=List[BaseStrategy], status_code=status.HTTP_200_OK
)
async def get_strategies(skip: int = 0, take: int = 50):
    strategies = await crud.get_strategies(database, skip, take)
    return [BaseStrategy.parse_obj(strategy) for strategy in strategies]


@app.get("/strategies/{id}", response_model=Strategy, status_code=status.HTTP_200_OK)
async def get_strategy(id: int):
    assets_per_strategy = await crud.get_strategy(database, id)
    date = assets_per_strategy[0]["date"]

    allocation = {}
    for a in assets_per_strategy:
        allocation[a["asset_id"]] = a["allocation"]

    strategy = Strategy(id=id, date=date, allocation=allocation)
    return strategy


@app.get(
    "/investments", response_model=List[Investment], status_code=status.HTTP_200_OK
)
async def get_investments(skip: int = 0, take: int = 50):
    investments = await crud.get_investments(database, skip, take)
    return [Investment.parse_obj(investment) for investment in investments]


@app.get("/investments/{id}", response_model=Investment, status_code=status.HTTP_200_OK)
async def get_investment(id: int):
    investment = await crud.get_investment(database, id)
    return Investment.parse_obj(investment)


@app.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
async def get_users(skip: int = 0, take: int = 50):
    users_to_investments = await crud.get_users(database, skip, take)
    users_to_investments = [
        UserInvestmentMapping.parse_obj(u) for u in users_to_investments
    ]
    us = users_to_investments.group_by(lambda x: x.user_id).map(
        lambda kv: (kv[0], kv[1].map(lambda i: i.investment_id))
    )
    return [
        User(id=user_id, investments_ids=investments)
        for user_id, investments in us.items()
    ]


@app.get("/users/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(id: int):
    investments_per_user = await crud.get_user(database, id)
    mapping = [UserInvestmentMapping.parse_obj(u) for u in investments_per_user]

    investments = mapping.map(lambda m: m.investment_id)

    return User(id=id, investments_ids=investments)
