import mysql.connector
from mysql.connector import pooling
from utils.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="tempshell_pool",
                pool_size=10,
                pool_reset_session=True,
                host=settings.DB_HOST,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                port=settings.DB_PORT,
                auth_plugin="mysql_native_password",
            )
            logger.info("Database connection pool created")
        return cls._pool

    @classmethod
    def get_connection(cls):
        return cls.get_pool().get_connection()


def init_db():
    """Create tables if they don't exist yet."""
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id                    INT PRIMARY KEY AUTO_INCREMENT,
                username              VARCHAR(63)  NOT NULL UNIQUE,
                password              VARCHAR(255) NOT NULL,
                email                 VARCHAR(127) NOT NULL UNIQUE,
                created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login            TIMESTAMP NULL,
                is_active             BOOLEAN DEFAULT TRUE,
                failed_login_attempts INT DEFAULT 0,
                locked_until          TIMESTAMP NULL,
                INDEX idx_username (username),
                INDEX idx_email    (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        conn.commit()
        logger.info("Database ready")
    finally:
        cursor.close()
        conn.close()
