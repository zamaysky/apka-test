import pydantic
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = pydantic.Field(alias="POSTGRES_USER")
    DB_PASSWORD: str = pydantic.Field(alias="POSTGRES_PASSWORD")
    DB_SERVER: str = pydantic.Field(alias="POSTGRES_HOST")
    DB_PORT: int = pydantic.Field(alias="POSTGRES_PORT")
    DB_NAME: str = pydantic.Field(alias="POSTGRES_DB_NAME")

    @property
    def asyncpg_conn(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()  # type: ignore
