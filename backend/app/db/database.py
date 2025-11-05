import mysql.connector
from mysql.connector import pooling
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database connection pool manager"""
    _connection_pool = None
    
    @classmethod
    def get_pool(cls):
        """Get or create connection pool"""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pooling.MySQLConnectionPool(
                    pool_name="tempshell_pool",
                    pool_size=10,
                    pool_reset_session=True,
                    host=settings.DB_HOST,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                    database=settings.DB_NAME,
                    port=settings.DB_PORT,
                    auth_plugin='mysql_native_password'
                )
                logger.info("Database connection pool created successfully")
            except Exception as e:
                logger.error(f"Failed to create connection pool: {e}")
                raise
        return cls._connection_pool
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        return cls.get_pool().get_connection()

def init_db():
    """Initialize database tables"""
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Create users table with security best practices
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(63) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(127) NOT NULL UNIQUE,
            shell_pod_id VARCHAR(100) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            is_active BOOLEAN DEFAULT TRUE,
            failed_login_attempts INT DEFAULT 0,
            locked_until TIMESTAMP NULL,
            INDEX idx_username (username),
            INDEX idx_email (email),
            INDEX idx_shell_pod_id (shell_pod_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_table_sql)
        conn.commit()
        logger.info("Database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
