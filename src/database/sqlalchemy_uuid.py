from uuid import UUID

from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.types import TypeDecorator


class SqlAlchemyUuid(TypeDecorator):
    """SQL Alchemy type for storing UUID as BINARY(16)"""
    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        try:
            return value.bytes
        except AttributeError:
            try:
                return UUID(value).bytes
            except TypeError:
                return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return UUID(bytes=value)

