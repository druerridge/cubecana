import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Shared base for all models
Base = declarative_base()

class DatabaseConnection:
    """
    Shared database connection manager used by all DAOs.
    Ensures only one connection pool is created for the entire application.
    """
    _instance = None
    _engine = None
    _Session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the database connection and session factory."""
        creds_file = Path('creds/creds.json')
        if creds_file.is_file():
            with creds_file.open() as f:
                creds_json = json.load(f)
                db_url = f"mysql://{creds_json['db_username']}:{creds_json['db_password']}@{creds_json['db_host']}/{creds_json['db_name']}?charset=utf8mb4"
        else:
            print(f"No creds file found at {creds_file.absolute()}, exiting")
            raise SystemExit(1)

        # Create a single connection pool for the entire application
        self._engine = create_engine(
            db_url,
            pool_size=1,
            max_overflow=4,
            pool_timeout=30,
            pool_recycle=900,
            pool_pre_ping=True
        )
        self._Session = scoped_session(sessionmaker(bind=self._engine))

    @property
    def engine(self):
        """Get the SQLAlchemy engine."""
        return self._engine

    @property
    def Session(self):
        """Get the scoped session factory."""
        return self._Session

    def get_session(self):
        """Create a new database session."""
        return self._Session()

# Singleton instance for the database connection
db_connection = DatabaseConnection()