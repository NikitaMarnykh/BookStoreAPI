from fastapi_filter.contrib.sqlalchemy import Filter

from src.book_operations.models_book import Book
from typing import Optional


# Фильтр книг (вхождение по строке для названия и автора, цена >= и <=)
class BookFilter(Filter):
    title__like: Optional[str | None] = None
    author__like: Optional[str | None] = None
    price__lte: Optional[int | None] = None
    price__gte: Optional[int | None] = None

    class Constants(Filter.Constants):
        model = Book
        search_field_name = ["title", "author", "price"]
