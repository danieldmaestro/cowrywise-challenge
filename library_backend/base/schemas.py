from typing import TypeVar, Generic, List, Optional, Any, Dict, Union

from ninja import Schema
from pydantic import BaseModel, Field, field_validator


class ResponseMsg(BaseModel):
    message: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


GenericResultsType = TypeVar("GenericResultsType")
DataT = TypeVar('DataT')


class GenericModel(BaseModel, Generic[DataT, GenericResultsType]):
    pass


class DefaultResponse(ResponseMsg, Generic[GenericResultsType]):
    data: GenericResultsType = None



class DictId(BaseModel):
    id: int = Field(ge=1)


class PageSchema(BaseModel, Generic[GenericResultsType]):
    total: int
    page_size: int
    page_index: int
    next: Optional[int]
    details: List[GenericResultsType]


class RequestPageSchema(BaseModel, Generic[GenericResultsType]):
    pending_count: int
    total: int
    page_size: int
    page_index: int
    next: int = Field(None)
    details: List[GenericResultsType]


class SimpleId(Schema):
    id: int


class PageFilter(Schema):
    page_index: int = 1
    page_size: int = Field(10, ge=1, le=100)
    ordering: str = Field(
        "", alias="ordering", description="sorting for multiple fields split with comma")

    @field_validator("page_index")
    def page_index_check(cls, page_index):
        if page_index <= 1:
            return 1
        return page_index

    def dict(
            self,
            *,
            exclude_none=True,
            exclude={"page_index", "page_size", "ordering"},
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
    ) -> Dict[str, Any]:
        return super().dict(
            exclude_none=exclude_none,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
        )
