from importlib.metadata import metadata

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData


class Base(DeclarativeBase):
    metadata = metadata
