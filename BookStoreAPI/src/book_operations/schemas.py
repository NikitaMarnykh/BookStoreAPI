from pydantic import BaseModel

# Какие значения будут требоваться при удалении книги(схема)
class BookDelete(BaseModel):
    id: int
    title: str
