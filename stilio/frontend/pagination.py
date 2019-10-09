from typing import List
import math

from stilio.frontend import settings as project_settings


def get_pages(count: int, current_page: int) -> List[int]:
    start_page = 1 if current_page < 5 else current_page - 4
    end_page = 8 + start_page

    total_pages = math.ceil(count / project_settings.PAGE_SIZE)
    end_page = total_pages if total_pages < end_page else end_page

    diff = start_page - end_page + 8

    start_page -= diff if (start_page - diff) > 1 else 0

    return [page for page in range(start_page, end_page + 1)]
