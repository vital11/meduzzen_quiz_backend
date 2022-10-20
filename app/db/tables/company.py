import sqlalchemy
from app.db.database import metadata


companies = sqlalchemy.Table(
    "companies",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
)
