from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default='logvision-backend', alias='APP_NAME')
    app_env: str = Field(default='dev', alias='APP_ENV')
    app_port: int = Field(default=8000, alias='APP_PORT')

    pg_host: str = Field(default='postgres', alias='PG_HOST')
    pg_port: int = Field(default=5432, alias='PG_PORT')
    pg_db: str = Field(default='logs', alias='PG_DB')
    pg_user: str = Field(default='logs_user', alias='PG_USER')
    pg_password: str = Field(default='logs_pass', alias='PG_PASSWORD')

    es_url: str = Field(default='http://elasticsearch:9200', alias='ES_URL')
    es_index: str = Field(default='log-unified-*', alias='ES_INDEX')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        return (
            f'postgresql+psycopg://{self.pg_user}:{self.pg_password}'
            f'@{self.pg_host}:{self.pg_port}/{self.pg_db}'
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
