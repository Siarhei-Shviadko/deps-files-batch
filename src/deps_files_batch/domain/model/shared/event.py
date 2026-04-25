from dataclasses import dataclass
from typing import Any

__all__ = ["Event"]


@dataclass
class Event:
    def recreate_enriched(self, **enrichment_kwargs: Any) -> "Event":
        event_kwargs = vars(self)
        event_kwargs.update(enrichment_kwargs)

        return self.__class__(**event_kwargs)
