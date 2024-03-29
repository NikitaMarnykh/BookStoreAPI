from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from fastapi_filter import FilterDepends

from src.book_operations.book_filter import BookFilter
from src.book_operations.fasta_api_for_protected_roter import fastapi_users


from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models_user import User
from src.database import get_async_session
from src.book_operations.models_book import Book
from src.image.crud import delete_image

from src.image.models_image import Image
from src.image import crud
from src.book_operations.schemas import BookDelete


router = APIRouter(
    prefix="/books",
    tags=["books"],
)


# JSON c данными о книгах (фильтр здесь, код для него books_filter)
# http://127.0.0.1:8000/docs/books/get_books
@router.get("/get_books")
async def get_books(book_filter: BookFilter = FilterDepends(BookFilter),
                    session: AsyncSession = Depends(get_async_session)):

    query = book_filter.filter(select(Book))
    result = await session.execute(query)
    return result.scalars().all()


# Получение данных о текущем пользователе
current_active_user: User = fastapi_users.current_user(active=True)


# Добавление новой книги
# http://127.0.0.1:8000/docs/books/protected-route/add_book
@router.post("/protected-route/add_book")
async def add_books(title: str = Form(), author: str = Form(), genre: str = Form(), price: float = Form(),
                    file: UploadFile = File(),
                    session: AsyncSession = Depends(get_async_session),
                    user: User = Depends(current_active_user)):
    book_id = await session.execute(select(Book).order_by(Book.id.desc()))
    bk_id = book_id.scalar()
    if bk_id is None:
        book_id = 0
    else:
        book_id = bk_id.id
    statement = await crud.add_image(book_id=book_id, image_file=file)
    await session.execute(statement)
    await session.commit()
    dict_new_book = {"title": title, "author": author, "genre": genre, "price": price, "owner_id": user.id}
    statement = insert(Book).values(**dict_new_book)
    await session.execute(statement)
    await session.commit()
    del session
    return True


# Удаление книг
# http://127.0.0.1:8000/docs/books/protected-route/delete_book
@router.delete("/protected-route/delete_book")
async def delete_book(book_delete: BookDelete,
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_active_user)):
    nd_img = await session.execute(select(Image).where(Image.book_id == book_delete.id))
    nd_bk = await session.execute(select(Book).where(Book.id == book_delete.id))
    nd_img, nd_bk = nd_img.scalar(), nd_bk.scalar()
    if nd_img is None or nd_bk is None:
        raise HTTPException(status_code=404, detail="No book found")
    else:
        image_name = nd_img.name
        book_id = nd_bk.id
        await delete_image(image_name=image_name, book_id=book_id)
        await session.delete(nd_bk)
        await session.delete(nd_img)
        await session.commit()
        del session
        return True
