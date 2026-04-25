from sqlalchemy.orm import declarative_base

from deps_files_batch.extras.database_session import metadata

__all__ = ["Base"]

Base = declarative_base(metadata=metadata)
