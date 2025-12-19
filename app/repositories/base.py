from cassandra.query import SimpleStatement
import uuid
from typing import Tuple, Any, Optional, Dict, List


class BaseRepository:
    table: str = ""
    select_cols: str = "*"
    prefix: str = ""

    def __init__(self, db):
        self.db = db

    def _get_session(self):
        session = self.db.get_session()
        if session is None:
            from ..exceptions import DatabaseError

            raise DatabaseError("Database session is not available")
        return session

    def list_with_search(
        self,
        page: int = 1,
        size: int = 10,
        q: Optional[Any] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Any], int]:

        if not self.table:
            raise ValueError("`table` must be provided either as argument or class attribute")

        session = self._get_session()

        if filters:
            clauses = []
            params = []
            for k, v in filters.items():
                clauses.append(f"{k} = %s")
                params.append(v)
            where = " AND ".join(clauses)
            query = SimpleStatement(f"SELECT {self.select_cols} FROM {self.table} WHERE {where}")
            rows = session.execute(query, tuple(params))
            items = list(rows)
            total = len(items)
            start = (page - 1) * size
            return items[start:start + size], total

        if q is not None:
            q_val = None
            is_uuid = False
            if isinstance(q, uuid.UUID):
                is_uuid = True
                q_val = q
            else:
                try:
                    q_val = uuid.UUID(str(q))
                    is_uuid = True
                except (ValueError, AttributeError, TypeError):
                    is_uuid = False

            if is_uuid:
                query = SimpleStatement(f"SELECT {self.select_cols} FROM {self.table} WHERE {self.prefix}_id = %s")
                rows = session.execute(query, (str(q_val),))
                items = list(rows)
                total = len(items)
                start = (page - 1) * size
                return items[start:start + size], total

            query = SimpleStatement(f"SELECT {self.select_cols} FROM {self.table} WHERE {self.prefix}_name = %s ALLOW FILTERING")
            rows = session.execute(query, (q,))
            items = list(rows)
            total = len(items)
            start = (page - 1) * size
            return items[start:start + size], total

        query = SimpleStatement(f"SELECT {self.select_cols} FROM {self.table}")
        rows = session.execute(query)
        items = list(rows)
        total = len(items)
        start = (page - 1) * size
        return items[start:start + size], total
