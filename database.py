import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    language TEXT DEFAULT 'ru',
                    ref_code TEXT UNIQUE,
                    referred_by INTEGER,
                    bonus_balance INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица талонов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS talons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    liters INTEGER NOT NULL,
                    price INTEGER NOT NULL,
                    status TEXT DEFAULT 'active',
                    qr_code_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                )
            """)
            
            # Таблица платежей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    talon_id INTEGER,
                    amount INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    tx_id TEXT,
                    confirmed_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (talon_id) REFERENCES talons (id)
                )
            """)
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def add_user(self, telegram_id: int, username: str = None, full_name: str = None, 
                      language: str = "ru", referred_by: int = None) -> bool:
        """Добавление нового пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Генерируем реферальный код
                ref_code = f"ref_{telegram_id}"
                
                await db.execute("""
                    INSERT OR IGNORE INTO users 
                    (telegram_id, username, full_name, language, ref_code, referred_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (telegram_id, username, full_name, language, ref_code, referred_by))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    async def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Получение пользователя по telegram_id"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def update_user_language(self, telegram_id: int, language: str) -> bool:
        """Обновление языка пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE users SET language = ? WHERE telegram_id = ?",
                    (language, telegram_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            return False
    
    async def create_talon(self, user_id: int, liters: int, price: int) -> Optional[int]:
        """Создание нового талона"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO talons (user_id, liters, price, status)
                    VALUES (?, ?, ?, 'pending')
                """, (user_id, liters, price))
                
                talon_id = cursor.lastrowid
                await db.commit()
                return talon_id
        except Exception as e:
            logger.error(f"Error creating talon: {e}")
            return None
    
    async def get_user_talons(self, user_id: int) -> List[Dict]:
        """Получение талонов пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM talons WHERE user_id = ? 
                    ORDER BY created_at DESC
                """, (user_id,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user talons: {e}")
            return []
    
    async def create_payment(self, user_id: int, talon_id: int, amount: int) -> Optional[int]:
        """Создание записи о платеже"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO payments (user_id, talon_id, amount, status)
                    VALUES (?, ?, ?, 'pending')
                """, (user_id, talon_id, amount))
                
                payment_id = cursor.lastrowid
                await db.commit()
                return payment_id
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            return None
    
    async def confirm_payment(self, payment_id: int, confirmed_by: int) -> bool:
        """Подтверждение платежа админом"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Обновляем статус платежа
                await db.execute("""
                    UPDATE payments 
                    SET status = 'confirmed', confirmed_by = ?, confirmed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (confirmed_by, payment_id))
                
                # Получаем talon_id для активации талона
                cursor = await db.execute(
                    "SELECT talon_id FROM payments WHERE id = ?", (payment_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    talon_id = row[0]
                    # Активируем талон
                    await db.execute("""
                        UPDATE talons SET status = 'active' WHERE id = ?
                    """, (talon_id,))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            return False
    
    async def get_pending_payments(self) -> List[Dict]:
        """Получение неподтвержденных платежей"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT p.*, u.username, u.full_name, t.liters
                    FROM payments p
                    JOIN users u ON p.user_id = u.telegram_id
                    JOIN talons t ON p.talon_id = t.id
                    WHERE p.status = 'pending'
                    ORDER BY p.created_at DESC
                """)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting pending payments: {e}")
            return []
    
    async def get_stats(self) -> Dict:
        """Получение статистики"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Общее количество пользователей
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                total_users = (await cursor.fetchone())[0]
                
                # Общее количество талонов
                cursor = await db.execute("SELECT COUNT(*) FROM talons WHERE status = 'active'")
                active_talons = (await cursor.fetchone())[0]
                
                # Общая выручка
                cursor = await db.execute("SELECT SUM(amount) FROM payments WHERE status = 'confirmed'")
                total_revenue = (await cursor.fetchone())[0] or 0
                
                # Количество продаж сегодня
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM payments 
                    WHERE status = 'confirmed' AND DATE(created_at) = DATE('now')
                """)
                today_sales = (await cursor.fetchone())[0]
                
                return {
                    "total_users": total_users,
                    "active_talons": active_talons,
                    "total_revenue": total_revenue,
                    "today_sales": today_sales
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    async def get_all_users(self) -> List[Dict]:
        """Получение всех пользователей"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT telegram_id, username, full_name, created_at 
                    FROM users ORDER BY created_at DESC
                """)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

# Глобальный экземпляр базы данных
db = Database()