# Import all the models, so that Base has them before being imported by Alembic

from app.db.database import metadata
from app.db.tables.user import users
from app.db.tables.company import companies
