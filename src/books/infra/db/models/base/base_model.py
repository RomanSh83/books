import re

from sqlalchemy.orm import DeclarativeBase, declared_attr


class BaseModel(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically generates the table name for the model.

        The table name is generated based on the class name by converting CamelCase to snake_case.
        """
        name = re.sub(pattern=r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", repl="_", string=cls.__name__)
        return name.lower()
