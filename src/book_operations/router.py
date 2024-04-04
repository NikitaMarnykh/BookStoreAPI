from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi_filter import FilterDepends

from src.book_operations.book_filter import BookFilter
from src.book_operations.fasta_api_for_protected_roter import fastapi_users


from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.auth.models_user import User
from src.book_operations.schemas import DeleteBook, ReadOneBook
from src.database import get_async_session
from src.book_operations.models_book import Book
from src.image.crud import delete_image, add_image

from src.image.models_image import Image
from src.image import crud


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
    del session
    return result.scalars().all()


@router.post("/get_books/{book_id}")
async def get_books(book_read: ReadOneBook, session: AsyncSession = Depends(get_async_session)):
    result = await session.get(Book, book_read.book_id)
    del session
    return result


# Получение данных о текущем пользователе
current_active_user: User = fastapi_users.current_user(active=True)


# Добавление новой книги
# http://127.0.0.1:8000/docs/books/protected-route/add_book
@router.post("/protected-route/add_book")
async def add_books(title: Optional[str | None] = Form(None),
                    author: Optional[str | None] = Form(None),
                    genre: Optional[str | None] = Form(None),
                    price: Optional[int | None] = Form(None),
                    file: UploadFile = File(None),
                    session: AsyncSession = Depends(get_async_session),
                    user: User = Depends(current_active_user)):
    book_id = await session.execute(select(Book).order_by(Book.id.desc()))
    bk_id = book_id.scalar()
    if bk_id is None:
        book_id = 1
    else:
        book_id = bk_id.id + 1
    image_dict = await crud.add_image(book_id=book_id, image_file=file)
    statement = insert(Image).values(**image_dict)
    await session.execute(statement)
    dict_new_book = {"title": title, "author": author, "genre": genre,
                     "price": price, "owner_id": user.id}
    statement = insert(Book).values(**dict_new_book)
    await session.execute(statement)
    await session.commit()
    del session
    return {"result": True}


# Удаление книг
# http://127.0.0.1:8000/docs/books/protected-route/delete_book
@router.delete("/protected-route/delete_book/{book_id}")
async def delete_book(book_delete: DeleteBook,
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_active_user)):
    nd_bk = await session.execute(select(Book).where(Book.id == book_delete.book_id).options(joinedload(Book.image)))
    nd_bk = nd_bk.scalar()

    if nd_bk is None:
        raise HTTPException(status_code=404, detail="The book was not found. Check the 'title' and 'id' parameters.")
    elif (nd_bk.owner_id != user.id) or (user.is_superuser is True):
        raise HTTPException(status_code=403, detail="You are not the owner of the book.")
    else:
        image_name = nd_bk.image.name
        await delete_image(image_name=image_name)
        await session.delete(nd_bk)
        await session.commit()
        del session
        return {"result": True}


# Изменение книги
# http://127.0.0.1:8000/docs/books/protected-route/update_book/{book_id}
@router.patch("/protected-route/update_book/{book_id}")
async def update_book(book_id: int,
                      title: Optional[str | None] = Form(None),
                      author: Optional[str | None] = Form(None),
                      genre: Optional[str | None] = Form(None),
                      price: Optional[int | None] = Form(None),
                      file: UploadFile = File(None),
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_active_user)):

    nd_bk = await session.execute(select(Book).where(Book.id == book_id).options(joinedload(Book.image)))
    nd_bk = nd_bk.scalar()
    if nd_bk is None:
        raise HTTPException(status_code=404, detail="The book was not found. Check the 'id' parameter.")
    elif (nd_bk.owner_id != user.id) or (user.is_superuser is True):
        raise HTTPException(status_code=403, detail="You are not the owner of the book.")
    else:
        if title is not None:
            nd_bk.title = title
        if author is not None:
            nd_bk.author = author
        if genre is not None:
            nd_bk.genre = genre
        if price is not None:
            nd_bk.price = price
        if file is not None:
            image_name = nd_bk.image.name
            book_id = nd_bk.id
            await delete_image(image_name=image_name)
            image_dict = await add_image(book_id=book_id, image_file=file)
            image = await session.get(Image, nd_bk.image.id)
            for key, value in image_dict.items():
                setattr(image, key, value)
        await session.commit()
        del session

        return {"result": True}
