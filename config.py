#!/usr/bin/env python3
"""
Конфигурация бота научного сообщества по продлению жизни
"""

import os

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8330707352:AAHu7P5s2waYJ65hlYTkvxtx_58ZxZSGak8')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///longevity_community.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Admin configuration
ADMIN_USERNAME = '@SilentGene'
ADMIN_IDS = [7667326674]  # Замените на ваш Telegram ID

# Scientific disciplines
SCIENTIFIC_DISCIPLINES = [
    "Молекулярная биология",
    "Клеточная биология", 
    "Генетика и геномика",
    "Биохимия",
    "Физиология человека",
    "Нейробиология и когнитивные науки",
    "Иммунология",
    "Геронтология и геронтогенетика",
    "Фармакология и биотехнологии",
    "Биоинформатика и вычислительная биология",
    "Синтетическая биология",
    "Системная биология",
    "Нанотехнологии и биоматериалы",
    "Биофизика",
    "Химия",
    "Математика и статистика",
    "Нейроинформатика и ИИ",
    "Медицинская практика",
    "Регуляторика и клинические испытания"
]

# Education levels
EDUCATION_LEVELS = [
    "Бакалавр",
    "Магистр", 
    "Аспирант",
    "Исследователь",
    "Преподаватель",
    "Доктор наук"
]

# Bot messages
WELCOME_MESSAGE = """
🔬 **Добро пожаловать в научное сообщество по продлению жизни!**

Мы ищем участников для научно-исследовательского проекта по продлению жизни и биомедицине!

🎯 **Цель проекта:**
Собрать сообщество молодых учёных и студентов разных дисциплин для регулярных онлайн-обсуждений научных статей по биологии старения, эпигенетике и применению ИИ в продлению жизни.

📋 **Что вас ждёт:**
• Междисциплинарные команды для обсуждения научных статей
• Регулярные онлайн-встречи и семинары
• Сетевые возможности для коллабораций
• Доступ к актуальным исследованиям в области долголетия

Для начала заполните анкету, чтобы мы могли подобрать вам подходящих коллег! 🚀
"""

# Database configuration
DB_CONFIG = {
    'users_table': 'users',
    'disciplines_table': 'disciplines', 
    'interests_table': 'interests',
    'matches_table': 'matches'
}

# Search configuration
SEARCH_CONFIG = {
    'max_results': 20,
    'min_match_score': 0.3,
    'interdisciplinary_threshold': 0.5
}

# Rate limiting
RATE_LIMITS = {
    'search_per_minute': 10,
    'search_per_hour': 50,
    'registration_per_day': 3
}
