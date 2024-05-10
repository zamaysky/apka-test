from contextlib import asynccontextmanager
from functools import partial

import aiofiles
import strawberry
from databases import Database
from fastapi import FastAPI
from jinja2 import Template
from strawberry.fastapi import BaseContext, GraphQLRouter
from strawberry.types import Info

from settings import settings


class Context(BaseContext):
    db: Database

    def __init__(
        self,
        db: Database,
    ) -> None:
        super().__init__()
        self.db = db



@strawberry.type
class Author:
    id: int
    name: str


@strawberry.type
class Book:
    id: int
    title: str
    author: Author


@strawberry.type
class Query:

    @strawberry.field
    async def books(
        self,
        info: Info[Context, None],
        author_ids: list[int] | None = None,
        search: str | None = None,
        limit: int | None = None,
    ) -> list[Book]:
        async with aiofiles.open("templates/books_query.tmpl") as file:
            template = Template(await file.read())
        query = template.render(author_ids=author_ids, search=search, limit=limit)
        books = await info.context.db.fetch_all(query)
        return [
            Book(
                id=book['id'],
                title=book['title'],
                author=Author(
                    id=book['author_id'],
                    name=book['author_name']),
            )
            for book in books
        ]



db = Database(
    settings.asyncpg_conn,
)

@asynccontextmanager
async def lifespan(
    app: FastAPI,
    db: Database,
):
    async with db:
        yield
    await db.disconnect()

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(  # type: ignore
    schema,
    context_getter=partial(Context, db),
)

app = FastAPI(lifespan=partial(lifespan, db=db))
app.include_router(graphql_app, prefix="/graphql")
