from src.config.settings import Settings


def test_settings_load_from_environment():
    settings = Settings()

    assert settings.postgres_db == "novastore"
    assert settings.postgres_user == "novastore"
    assert settings.postgres_password.get_secret_value()
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432


def test_database_url():
    settings = Settings()
    database_url = settings.database_url

    assert database_url.drivername == "postgresql+psycopg"
    assert database_url.host == "localhost"
    assert database_url.port == 5432
    assert database_url.database == "novastore"
