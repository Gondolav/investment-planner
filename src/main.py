import pyfuncol
from typing import List
import databases
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from . import crud
from .models import (
    Asset,
    AssetIn,
    BaseStrategy,
    BaseUser,
    Investment,
    InvestmentIn,
    Location,
    LocationIn,
    Message,
    Strategy,
    StrategyIn,
    User,
    UserIn,
)
from .config import DATABASE_URL


database = databases.Database(DATABASE_URL, min_size=1, max_size=5)

app = FastAPI(title="Investment planner")

origins = [
    "https://investment-planner.onrender.com",
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


@app.get("/locations", response_model=List[Location], status_code=status.HTTP_200_OK)
async def get_locations(skip: int = 0, take: int = 50):
    locations = await crud.get_locations(database, skip, take)
    return [Location.parse_obj(location) for location in locations]


@app.get(
    "/locations/{id}",
    response_model=Location,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
)
async def get_location(id: int):
    location = await crud.get_location(database, id)
    if not location:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Location not found"},
        )
    return Location.parse_obj(location)


@app.post("/locations", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_location(location: LocationIn):
    id = await crud.insert_location(database, location)
    return id


@app.get("/assets", response_model=List[Asset], status_code=status.HTTP_200_OK)
async def get_assets(skip: int = 0, take: int = 50):
    assets = await crud.get_assets(database, skip, take)
    return [Asset.parse_obj(asset) for asset in assets]


@app.get(
    "/assets/{id}",
    response_model=Asset,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
)
async def get_asset(id: int):
    asset = await crud.get_asset(database, id)
    if not asset:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Asset not found"},
        )
    return Asset.parse_obj(asset)


@app.post("/assets", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_asset(asset: AssetIn):
    id = await crud.insert_asset(database, asset)
    return id


@app.get(
    "/strategies", response_model=List[BaseStrategy], status_code=status.HTTP_200_OK
)
async def get_strategies(skip: int = 0, take: int = 50):
    strategies = await crud.get_strategies(database, skip, take)
    return [BaseStrategy.parse_obj(strategy) for strategy in strategies]


@app.get(
    "/strategies/{id}",
    response_model=Strategy,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
)
async def get_strategy(id: int):
    assets_per_strategy = await crud.get_strategy(database, id)
    if not assets_per_strategy:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Strategy not found"},
        )

    date = assets_per_strategy[0]["date"]

    allocation = {}
    for a in assets_per_strategy:
        allocation[a["asset_id"]] = a["allocation"]

    strategy = Strategy(id=id, date=date, allocation=allocation)
    return strategy


@app.post("/strategies", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy: StrategyIn):
    id = await crud.insert_strategy(database, strategy)
    return id


@app.get(
    "/investments", response_model=List[Investment], status_code=status.HTTP_200_OK
)
async def get_investments(skip: int = 0, take: int = 50):
    investments = await crud.get_investments(database, skip, take)
    return [Investment.parse_obj(investment) for investment in investments]


@app.get(
    "/investments/{id}",
    response_model=Investment,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
)
async def get_investment(id: int):
    investment = await crud.get_investment(database, id)
    if not investment:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Investment not found"},
        )

    return Investment.parse_obj(investment)


@app.post("/investments", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_investment(investment: InvestmentIn, user_id: int):
    id = await crud.insert_investment(database, investment, user_id)
    return id


@app.get("/users", response_model=List[BaseUser], status_code=status.HTTP_200_OK)
async def get_users(skip: int = 0, take: int = 50):
    users = await crud.get_users(database, skip, take)
    return [BaseUser.parse_obj(user) for user in users]


@app.get(
    "/users/{id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
)
async def get_user(id: int):
    investments_per_user = await crud.get_user(database, id)
    if not investments_per_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "User not found"},
        )

    username = investments_per_user[0]["username"]

    investments = [i["investment_id"] for i in investments_per_user]
    investments = [] if not all(investments) else investments

    return User(id=id, name=username, investments_ids=investments)


@app.post("/users", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn):
    id = await crud.insert_user(database, user)
    return id
