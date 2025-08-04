
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import (
    Column, DateTime
)
from sqlalchemy.ext.declarative import declarative_base


class Base(object):
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
    deleted_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=True
    )

DeclarativeBase = declarative_base(cls=Base)