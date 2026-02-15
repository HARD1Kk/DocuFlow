from pydantic.settings import BaseSettings


class documents(BaseSettings):
    documents:list[str]
