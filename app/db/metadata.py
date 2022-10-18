# Import all the models, so that Base has them before being imported by Alembic

# from app.db.database import Base
# from app.models.user_item import User, Item

from app.db.database import metadata
from app.models.user import users
from app.models.company import companies

