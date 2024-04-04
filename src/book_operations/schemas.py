from pydantic import BaseModel


class ReadOneBook(BaseModel):
    book_id: int


class DeleteBook(BaseModel):
    book_id: int
