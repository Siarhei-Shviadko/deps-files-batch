from deps_files_batch.domain.model import Group, ICommandGroupRepository

__all__ = ["FakeCommandGroupRepository"]


class FakeCommandGroupRepository(ICommandGroupRepository):
    def __init__(self) -> None:
        self._db: dict[tuple[str, str], Group] = {}
        self._document_types: set[str] = set()

    def group_of_id(self, group_id: str, tenant_id: str) -> Group | None:
        group = self._db.get((group_id, tenant_id))

        if group and not group.is_deleted:
            return group

        return None

    def save(self, group: Group) -> None:
        self._db[(group.id(), group.tenant_id())] = group

    def save_all(self, groups: list[Group]) -> None:
        for group in groups:
            self.save(group)

    def delete(self, group: Group) -> None:
        self.save(group)

    def save_document_types(self, document_type_ids: list[str]) -> None:
        self._document_types.update(document_type_ids)

    def delete_document_type(self, document_type_id: str) -> None:
        self._document_types.discard(document_type_id)

        for group in self._db.values():
            group.document_types = [dt for dt in group.document_types if dt() != document_type_id]
