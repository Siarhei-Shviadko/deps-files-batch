from .configured_base_serializer import ConfiguredSerializer

__all__ = [
    "PaginatedResultMetadataSerializer",
]


class PaginatedResultMetadataSerializer(ConfiguredSerializer):
    size: int
    total: int
