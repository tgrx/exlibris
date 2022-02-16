from typing import List
from typing import Optional

from consigliere import telegram
from sqlalchemy import and_
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.engine import Row

from main import db
from main.util import to_values


async def install_user(
    session: db.Session,
    *,
    user: telegram.User,
) -> db.User:
    """
    Registers an user: creates it if not exist otherwise updates it.
    :param session: database session
    :param user: telegram user
    :return: database user
    """

    values_to_update = to_values(
        {
            db.User.first_name: user.first_name,
            db.User.is_bot: user.is_bot,
            db.User.last_name: user.last_name,
            db.User.username: user.username,
        }
    )

    values_to_insert = to_values(
        {
            db.User.tg_id: user.id,
            **values_to_update,
        }
    )

    query = (
        insert(db.User)
        .values(**values_to_insert)
        .on_conflict_do_update(
            constraint=db.User.__table_args__[0].name,
            set_=values_to_update,
        )
        .returning(db.User)
    )

    cursor: CursorResult = await session.execute(query)
    row: Row = cursor.one()
    dbo = db.User(**row)

    return dbo


async def get_unbound_raws(
    session: db.Session,
    *,
    user: db.User,
) -> List[db.Raw]:
    """
    Returns RAWs which are bound to no book
    :param session: db session
    :param user: db user
    :return: list of db RAWs
    """

    query = select(db.Raw).where(
        and_(
            db.Raw.book_id.is_(None),
            db.Raw.user_id == user.id,
        )
    )

    cursor: CursorResult = await session.execute(query)
    dbo_list: List[db.Raw] = cursor.scalars().all()

    return dbo_list


async def install_raw(
    session: db.Session,
    *,
    description: Optional[str] = None,
    message_id: int,
    photo_file_id: Optional[str] = None,
    user: db.User,
) -> db.Raw:
    """
    Creates a new RAW or updates existing one against (user, message_id)
    :param session: db session
    :param description: any text content
    :param message_id: telegram message id
    :param photo_file_id: telegram file id
    :param user: db user
    :return: db RAW
    """

    values_to_update = to_values(
        {
            db.Raw.description: description,
            db.Raw.photo_file_id: photo_file_id,
        }
    )

    values_to_insert = to_values(
        {
            db.Raw.user_id: user.id,
            db.Raw.message_id: message_id,
            **values_to_update,
        }
    )

    query = (
        insert(db.Raw)
        .values(**values_to_insert)
        .on_conflict_do_update(
            constraint=db.Raw.__table_args__[0].name,
            set_=values_to_update,
        )
        .returning(db.Raw)
    )

    cursor: CursorResult = await session.execute(query)
    row: Row = cursor.one()
    dbo = db.Raw(**row)

    return dbo


async def remove_unbound_raws(
    session: db.Session,
    *,
    user: db.User,
) -> List[db.Raw]:
    """
    Removes unbound RAWs for given user
    :param session: db session
    :param user: db user
    :return: list of deleted RAWs
    """

    query = (
        delete(db.Raw)
        .where(
            and_(
                db.Raw.book_id.is_(None),
                db.Raw.user_id == user.id,
            )
        )
        .returning(db.Raw)
    )

    cursor: CursorResult = await session.execute(query)
    rows: List[Row] = cursor.fetchall()
    dbo_list = [db.Raw(**row) for row in rows]

    return dbo_list


async def create_book(
    session: db.Session,
    *,
    user: db.User,
) -> db.Book:
    """
    Creates and returns a new db book
    :param session: db session
    :param user: db user
    :return: db book
    """

    values_to_insert = to_values(
        {
            db.Book.user_id: user.id,
        }
    )

    query = insert(db.Book).values(**values_to_insert).returning(db.Book)

    cursor: CursorResult = await session.execute(query)
    row: Row = cursor.one()
    dbo = db.Book(**row)

    await bound_raws(session, book=dbo)

    return dbo


async def bound_raws(session: db.Session, *, book: db.Book) -> List[db.Raw]:
    """
    Bounds unbound RAWs to given book
    :param session: db session
    :param book: db book
    :return: list of bound db raws
    """

    query = (
        update(db.Raw)
        .where(
            and_(
                db.Raw.book_id.is_(None),
                db.Raw.user_id == book.user_id,
            )
        )
        .values(
            **to_values(
                {
                    db.Raw.book_id: book.id,
                }
            )
        )
        .returning(db.Raw)
    )

    cursor: CursorResult = await session.execute(query)
    rows: List[Row] = cursor.fetchall()
    dbo_list = [db.Raw(**row) for row in rows]

    return dbo_list
