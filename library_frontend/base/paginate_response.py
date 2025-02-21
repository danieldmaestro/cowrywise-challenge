from django.core.paginator import Paginator
from django.db.models import QuerySet

from base.schemas import PageSchema, GenericResultsType
from base.schemas import PageFilter


def get_page(
        queryset: QuerySet,
        pager_filter: PageFilter,
        generic_result_type: GenericResultsType
) -> PageSchema:
    p = Paginator(queryset, per_page=pager_filter.page_size).get_page(pager_filter.page_index)

    start = (p.number - 1) * p.paginator.per_page
    count = queryset.count()
    next = 0

    if start + p.paginator.per_page < count:
        next = p.number + 1

    data = PageSchema[generic_result_type](
        total=p.paginator.count,
        page_size=p.paginator.per_page,
        page_index=p.number,
        next=next,
        details=list(p.object_list)
    )
    return data