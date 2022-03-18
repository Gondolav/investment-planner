import sqlalchemy

from .config import DATABASE_URL

metadata = sqlalchemy.MetaData()

assets = sqlalchemy.Table(
    "Asset",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("name", sqlalchemy.String, index=True),
    sqlalchemy.Column("apr", sqlalchemy.Float),
    sqlalchemy.Column("risk", sqlalchemy.Integer),
)

strategies = sqlalchemy.Table(
    "Strategy",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("date", sqlalchemy.Date, index=True),
)

assets_per_strategy = sqlalchemy.Table(
    "AssetStrategy",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column(
        "strategy_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("Strategy.id")
    ),
    sqlalchemy.Column(
        "asset_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("Asset.id")
    ),
    sqlalchemy.Column("allocation", sqlalchemy.Float),
)

investments = sqlalchemy.Table(
    "Investment",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("amount", sqlalchemy.Float),
    sqlalchemy.Column(
        "strategy_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("Strategy.id")
    ),
    sqlalchemy.Column("date", sqlalchemy.Date, index=True),
)

users = sqlalchemy.Table(
    "User",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, index=True),
    sqlalchemy.Column(
        "investment_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("Investment.id")
    ),
)

engine = sqlalchemy.create_engine(DATABASE_URL, pool_size=3, max_overflow=0)

metadata.create_all(engine)
