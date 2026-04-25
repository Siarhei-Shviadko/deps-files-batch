from sqlalchemy import and_, select

from deps_files_batch.domain.model import IQueryGroupRepository
from deps_files_batch.extras import DatabaseSession

from ..tables import group_table

__all__ = ["QueryGroupRepository"]


class QueryGroupRepository(IQueryGroupRepository):
    def __init__(self, database: DatabaseSession) -> None:
        self._db = database

    def exists_group_of_id(self, group_id: str, tenant_id: str) -> bool:
        query = select(group_table.c.group_id).where(
            and_(
                group_table.c.group_id == group_id,
                group_table.c.tenant_id == tenant_id,
                group_table.c.is_deleted.is_(False),
            ),
        )

        with self._db.connection() as conn:
            result = conn.execute(query).fetchone()

        return result is not None
