from databases import Database
from sqlalchemy import select

from .models import AssetIn, InvestmentIn, StrategyIn, UserIn

from .db import (
    assets,
    assets_per_strategy,
    strategies,
    investments,
    users,
    investments_per_user,
)


def get_assets(db: Database, skip: int = 0, take: int = 50):
    query = assets.select().offset(skip).limit(take)
    return db.fetch_all(query)


def get_asset(db: Database, id: int):
    query = assets.select().where(assets.c.id == id)
    return db.fetch_one(query)


def insert_asset(db: Database, asset: AssetIn):
    query = assets.insert().values(name=asset.name, apr=asset.apr, risk=asset.risk)
    return db.execute(query)


def get_strategies(db: Database, skip: int = 0, take: int = 50):
    query = strategies.select().offset(skip).limit(take)
    return db.fetch_all(query)


def get_strategy(db: Database, id: int):
    query = select(
        strategies.c.id,
        strategies.c.date,
        assets_per_strategy.c.asset_id,
        assets_per_strategy.c.allocation,
    ).select_from(
        strategies.join(assets_per_strategy, assets_per_strategy.c.strategy_id == id)
    )
    return db.fetch_all(query)


async def insert_strategy(db: Database, strategy: StrategyIn):
    async with db.transaction():
        query = strategies.insert().values(date=strategy.date)
        strategy_id = await db.execute(query)

        values = [
            {"strategy_id": strategy_id, "asset_id": asset_id, "allocation": allocation}
            for asset_id, allocation in strategy.allocation.items()
        ]
        await db.execute_many(query=assets_per_strategy.insert(), values=values)

        return strategy_id


def get_investments(db: Database, skip: int = 0, take: int = 50):
    query = investments.select().offset(skip).limit(take)
    return db.fetch_all(query)


def get_investment(db: Database, id: int):
    query = investments.select().where(investments.c.id == id)
    return db.fetch_one(query)


async def insert_investment(db: Database, investment: InvestmentIn, user_id: int):
    async with db.transaction():
        query = investments.insert().values(
            amount=investment.amount,
            strategy_id=investment.strategy_id,
            date=investment.date,
        )
        investment_id = await db.execute(query)

        query = investments_per_user.insert().values(
            user_id=user_id, investment_id=investment_id
        )
        await db.execute(query)

        return investment_id


def get_users(db: Database, skip: int = 0, take: int = 50):
    query = users.select().offset(skip).limit(take)
    return db.fetch_all(query)


async def get_user(db: Database, id: int):
    query = select(users.c.username, investments_per_user.c.investment_id,).select_from(
        users.join(investments_per_user, investments_per_user.c.user_id == id)
    )

    investments = await db.fetch_all(query)

    if not investments:
        query = users.select().where(users.c.id == id)
        user = await db.fetch_one(query)
        return [{"username": user["username"], "investment_id": None}]
    else:
        return investments


def insert_user(db: Database, user: UserIn):
    query = users.insert().values(username=user.name)
    return db.execute(query)
