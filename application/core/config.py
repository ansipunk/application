import pydantic_settings


class PostgresSettings(pydantic_settings.BaseSettings):
    host: str = "127.0.0.1"
    port: int = 5432
    user: str = "application"
    password: str = "application"
    database: str = "application"
    force_rollback: bool = False

    @property
    def url(self) -> str:
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="application_postgres_",
    )


class WebSettings(pydantic_settings.BaseSettings):
    debug: bool = False
    api_key: str = "000-000-000"

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="application_web_",
    )


postgres = PostgresSettings()
web = WebSettings()
