from .base import BusinessException, NotFoundError

__all__ = ["GroupNotFound", "GroupDoesntContainDocumentTypes"]


class GroupNotFound(NotFoundError):
    code = "group_not_found"

    def __init__(self, group_id: str) -> None:
        super().__init__(f"Group with id `{group_id}` not found.")


class GroupDoesntContainDocumentTypes(BusinessException):
    code = "group_doesnt_contain_document_types"

    def __init__(self, group_id: str) -> None:
        super().__init__(f"Attempting to create a file with wrong document_type for group `{group_id}`.")
