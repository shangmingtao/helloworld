"""
数据库配置模块
"""
import pymysql
from typing import Optional

class DatabaseConfig:
    """数据库配置类"""
    HOST = "t4ptuv8y87azk.oceanbase.aliyuncs.com"
    USER = "test_seal_stock"
    PASSWORD = "test_seal_stock@2023"
    DATABASE = "test_seal_stock2"
    
    @classmethod
    def get_connection(cls) -> pymysql.Connection:
        """获取数据库连接"""
        return pymysql.connect(
            host=cls.HOST,
            user=cls.USER,
            passwd=cls.PASSWORD,
            database=cls.DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )

class UserModel:
    """用户数据模型"""
    
    """
    假设用户表已存在，表结构如下：
    CREATE TABLE `users` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `username` varchar(50) NOT NULL UNIQUE COMMENT '用户名',
        `password` varchar(255) NOT NULL COMMENT '密码(加密存储)',
        `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
        `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        `is_active` tinyint(1) DEFAULT 1 COMMENT '是否激活(1:激活,0:禁用)',
        PRIMARY KEY (`id`),
        KEY `idx_username` (`username`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
    """
    
    @staticmethod
    def create_user(username: str, password: str, email: str = None) -> bool:
        """创建用户"""
        try:
            with DatabaseConfig.get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (username, password, email))
                    conn.commit()
                    return True
        except pymysql.IntegrityError:
            # 用户名已存在
            return False
        except Exception as e:
            print(f"创建用户失败: {e}")
            return False
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[dict]:
        """根据用户名获取用户信息"""
        try:
            with DatabaseConfig.get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM users WHERE username = %s AND is_active = 1"
                    cursor.execute(sql, (username,))
                    return cursor.fetchone()
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    @staticmethod
    def verify_user(username: str, password: str) -> Optional[dict]:
        """验证用户登录"""
        user = UserModel.get_user_by_username(username)
        if user and user['password'] == password:  # 实际项目中应该使用密码哈希验证
            return user
        return None