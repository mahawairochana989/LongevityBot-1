#!/usr/bin/env python3
"""
База данных для бота научного сообщества по продлению жизни
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import DB_CONFIG

logger = logging.getLogger(__name__)

class LongevityDatabase:
    """
    Класс для работы с базой данных научного сообщества
    """
    
    def __init__(self, db_path: str = "longevity_community.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {DB_CONFIG['users_table']} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER UNIQUE NOT NULL,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        name TEXT NOT NULL,
                        university TEXT,
                        discipline TEXT,
                        interests TEXT,
                        education_level TEXT,
                        contact_info TEXT,
                        avatar_url TEXT,
                        telegram_profile TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Таблица дисциплин
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {DB_CONFIG['disciplines_table']} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        keywords TEXT
                    )
                """)
                
                # Таблица интересов
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {DB_CONFIG['interests_table']} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        interest TEXT,
                        FOREIGN KEY (user_id) REFERENCES {DB_CONFIG['users_table']} (id)
                    )
                """)
                
                # Таблица совпадений
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {DB_CONFIG['matches_table']} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user1_id INTEGER,
                        user2_id INTEGER,
                        match_score REAL,
                        common_interests TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user1_id) REFERENCES {DB_CONFIG['users_table']} (id),
                        FOREIGN KEY (user2_id) REFERENCES {DB_CONFIG['users_table']} (id)
                    )
                """)

                # Личный нейронаучный журнал Nimbus Academy
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS neuroscience_journal_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER NOT NULL,
                        module_id TEXT NOT NULL,
                        prompt TEXT NOT NULL,
                        response TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("База данных инициализирована успешно")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def add_user(self, user_data: Dict) -> bool:
        """Добавление пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {DB_CONFIG['users_table']} 
                    (telegram_id, username, first_name, last_name, name, university, 
                     discipline, interests, education_level, contact_info, avatar_url, 
                     telegram_profile, is_active, last_activity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                """, (
                    user_data.get('telegram_id'),
                    user_data.get('username'),
                    user_data.get('first_name'),
                    user_data.get('last_name'),
                    user_data.get('name'),
                    user_data.get('university'),
                    user_data.get('discipline'),
                    user_data.get('interests'),
                    user_data.get('education_level'),
                    user_data.get('contact_info'),
                    user_data.get('avatar_url'),
                    user_data.get('telegram_profile')
                ))
                
                # Добавляем интересы
                user_id = cursor.lastrowid
                if user_data.get('interests_list'):
                    for interest in user_data['interests_list']:
                        cursor.execute(f"""
                            INSERT INTO {DB_CONFIG['interests_table']} (user_id, interest)
                            VALUES (?, ?)
                        """, (user_id, interest))
                
                conn.commit()
                logger.info(f"Пользователь {user_data.get('name')} добавлен в базу данных")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
            return False
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Получение пользователя по telegram_id"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    SELECT * FROM {DB_CONFIG['users_table']} 
                    WHERE telegram_id = ? AND is_active = 1
                """, (telegram_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None
    
    def search_users(self, query: str, discipline: str = None, limit: int = 20) -> List[Dict]:
        """Поиск пользователей по запросу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Базовый запрос
                sql = f"""
                    SELECT * FROM {DB_CONFIG['users_table']} 
                    WHERE is_active = 1
                """
                params = []
                
                # Добавляем условия поиска
                if query:
                    sql += " AND (name LIKE ? OR interests LIKE ? OR university LIKE ?)"
                    search_term = f"%{query}%"
                    params.extend([search_term, search_term, search_term])
                
                if discipline:
                    sql += " AND discipline = ?"
                    params.append(discipline)
                
                sql += " ORDER BY last_activity DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка поиска пользователей: {e}")
            return []
    
    def get_all_users(self, admin_only: bool = False) -> List[Dict]:
        """Получение всех пользователей (только для админов)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    SELECT * FROM {DB_CONFIG['users_table']} 
                    WHERE is_active = 1
                    ORDER BY registration_date DESC
                """)
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка получения всех пользователей: {e}")
            return []
    
    def find_matches(self, user_id: int, interdisciplinary: bool = False) -> List[Dict]:
        """Поиск совпадений для пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем данные пользователя
                cursor.execute(f"""
                    SELECT * FROM {DB_CONFIG['users_table']} 
                    WHERE id = ?
                """, (user_id,))
                
                user = cursor.fetchone()
                if not user:
                    return []
                
                user_columns = [description[0] for description in cursor.description]
                user_data = dict(zip(user_columns, user))
                
                # Ищем совпадения
                sql = f"""
                    SELECT u.*, 
                           CASE 
                               WHEN u.discipline = ? THEN 0.3
                               WHEN u.interests LIKE ? THEN 0.5
                               ELSE 0.1
                           END as match_score
                    FROM {DB_CONFIG['users_table']} u
                    WHERE u.id != ? AND u.is_active = 1
                """
                params = [user_data['discipline'], f"%{user_data.get('interests', '')}%", user_id]
                
                if not interdisciplinary:
                    sql += " AND u.discipline = ?"
                    params.append(user_data['discipline'])
                
                sql += " ORDER BY match_score DESC, u.last_activity DESC LIMIT 10"
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка поиска совпадений: {e}")
            return []

    def add_journal_entry(self, telegram_id: int, module_id: str, prompt: str, response: str) -> bool:
        """Сохранение ответа студента в личный нейронаучный журнал."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO neuroscience_journal_entries
                    (telegram_id, module_id, prompt, response)
                    VALUES (?, ?, ?, ?)
                """, (telegram_id, module_id, prompt, response))

                conn.commit()
                logger.info(
                    "Запись нейронаучного журнала сохранена: user=%s module=%s",
                    telegram_id,
                    module_id,
                )
                return True

        except Exception as e:
            logger.error(f"Ошибка сохранения записи нейронаучного журнала: {e}")
            return False

    def get_journal_entries(self, telegram_id: int) -> List[Dict]:
        """Получение записей личного нейронаучного журнала студента."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, module_id, prompt, response, created_at
                    FROM neuroscience_journal_entries
                    WHERE telegram_id = ?
                    ORDER BY created_at DESC
                """, (telegram_id,))

                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error(f"Ошибка получения нейронаучного журнала: {e}")
            return []
    
    def update_user_activity(self, telegram_id: int):
        """Обновление времени последней активности"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    UPDATE {DB_CONFIG['users_table']} 
                    SET last_activity = CURRENT_TIMESTAMP 
                    WHERE telegram_id = ?
                """, (telegram_id,))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Ошибка обновления активности: {e}")
    
    def get_statistics(self) -> Dict:
        """Получение статистики сообщества"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общее количество пользователей
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {DB_CONFIG['users_table']} 
                    WHERE is_active = 1
                """)
                total_users = cursor.fetchone()[0]
                
                # Пользователи по дисциплинам
                cursor.execute(f"""
                    SELECT discipline, COUNT(*) as count 
                    FROM {DB_CONFIG['users_table']} 
                    WHERE is_active = 1 AND discipline IS NOT NULL
                    GROUP BY discipline
                    ORDER BY count DESC
                """)
                disciplines = cursor.fetchall()
                
                # Активные пользователи за последние 7 дней
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {DB_CONFIG['users_table']} 
                    WHERE is_active = 1 AND last_activity > datetime('now', '-7 days')
                """)
                active_users = cursor.fetchone()[0]
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'disciplines': disciplines
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def export_to_csv(self) -> str:
        """Экспорт данных в CSV"""
        try:
            import csv
            import io
            
            users = self.get_all_users()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Заголовки
            if users:
                writer.writerow(users[0].keys())
                
                # Данные
                for user in users:
                    writer.writerow(user.values())
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка экспорта в CSV: {e}")
            return ""
