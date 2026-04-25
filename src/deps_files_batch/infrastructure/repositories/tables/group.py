from sqlalchemy import Boolean, Column, ForeignKey, String, Table

from deps_files_batch.extras import metadata

__all__ = ["group_table", "group_document_types_table"]

group_table = Table(
    "group",
    metadata,
    Column("group_id", String, primary_key=True),
    Column("tenant_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("is_deleted", Boolean, nullable=False),
)

group_document_types_table = Table(
    "group_document_types",
    metadata,
    Column(
        "group_id",
        String,
        ForeignKey("group.group_id", ondelete="cascade", name="group_id_fk"),
        primary_key=True,
    ),
    Column("document_type_id", String, ForeignKey("document_type.id"), nullable=False, primary_key=True),
)
