"""Base repository utilities for Cassandra-backed repositories.

This module provides `BaseRepository`, a small helper class that wraps
access to a Cassandra session and exposes a common `list_with_search`
method used by concrete repository implementations.

The class is intentionally lightweight: concrete repositories set the
`table` and `prefix` class attributes and reuse the provided `db`
connection object.
"""

from cassandra.query import SimpleStatement
import uuid
from typing import Tuple, Any, Optional, Dict, List

class BaseRepository:
  """Common repository base for simple Cassandra queries.

  Attributes:
  - `table` (str): target Cassandra table name; must be provided by
      subclasses.
  - `select_cols` (str): columns to select in queries (defaults to
      "*").
  - `prefix` (str): prefix used for id/name column naming in queries
      (e.g. `student` -> `student_id`, `student_name`).

  The repository expects a `db` object with a `get_session()` method
  returning a live Cassandra session.
  """

  table: str = ""
  select_cols: str = "*"
  prefix: str = ""

  def __init__(self, db):
    """Initialize repository with a database connection object.

    Args:
            db: Database connection wrapper exposing `get_session()`.
    """
    self.db = db

  def _get_session(self):
      """Return an active Cassandra session or raise `DatabaseError`.

      This helper centralizes the check for session availability so
      callers can assume a valid session object is returned.
      """
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
    """List rows from the repository table with optional search/filter.

    The method supports three modes:
    - `filters` provided: builds a WHERE clause from key/value pairs.
    - `q` provided and is a UUID: searches by `{prefix}_id`.
    - `q` provided and not a UUID: searches by `{prefix}_name` (uses
      `ALLOW FILTERING`).

    Pagination is applied in-memory using `page` and `size`.

    Args:
        page: 1-based page number.
        size: number of items per page.
        q: optional query value (UUID or string) used for simple
            search by id or name depending on its type.
        filters: optional mapping of column -> value for exact
                  filtering.

    Returns:
        A tuple `(items, total)` where `items` is the list of rows
        for the requested page and `total` is the total number of
        rows matching the query.
    """

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
