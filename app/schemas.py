"""Request and response schemas for blogs."""

from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

NonBlankStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class BlogCreate(BaseModel):
    """Fields required to create a blog."""

    model_config = ConfigDict(extra="forbid")

    title: NonBlankStr
    content: NonBlankStr


class BlogUpdate(BaseModel):
    """Fields that may be changed on a blog; omitted fields are left untouched."""

    model_config = ConfigDict(extra="forbid")

    title: NonBlankStr | None = None
    content: NonBlankStr | None = None

    @model_validator(mode="after")
    def _require_non_null_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one of title or content must be provided")
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} must not be null")
        return self


class BlogRead(BaseModel):
    """A blog as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
