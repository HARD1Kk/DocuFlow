from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str
    AZURE_OPENAI_API_VERSION: str
    # Azure Chat Config
    AZURE_CHATOPENAI_API_KEY: str
    AZURE_CHATOPENAI_ENDPOINT: str
    AZURE_CHATOPENAI_DEPLOYMENT: str
    AZURE_CHATOPENAI_API_VERSION: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# INSTANTIATION
settings = Settings()
