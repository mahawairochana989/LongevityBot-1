#!/usr/bin/env python3
"""
Основной файл бота научного сообщества по продлению жизни
"""

import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, WELCOME_MESSAGE, ADMIN_IDS, ADMIN_USERNAME, SCIENTIFIC_DISCIPLINES, EDUCATION_LEVELS
from database import LongevityDatabase

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Состояния регистрации
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_university = State()
    waiting_for_discipline = State()
    waiting_for_interests = State()
    waiting_for_education_level = State()
    waiting_for_contact = State()

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация базы данных
db = LongevityDatabase()

# Проверка админа
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Обработка команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    """Обработка команды /start"""
    try:
        # Проверяем, зарегистрирован ли пользователь
        user = db.get_user(message.from_user.id)
        
        if user:
            # Пользователь уже зарегистрирован
            if is_admin(message.from_user.id):
                # Администратор - полный доступ
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="🔍 Найти коллег", callback_data="find_colleagues")],
                    [types.InlineKeyboardButton(text="👥 Междисциплинарные команды", callback_data="interdisciplinary_teams")],
                    [types.InlineKeyboardButton(text="📊 Статистика сообщества", callback_data="community_stats")],
                    [types.InlineKeyboardButton(text="🎯 Рекомендации", callback_data="recommendations")]
                ])
            else:
                # Обычный пользователь - ограниченный доступ
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="📊 Статистика сообщества", callback_data="community_stats")],
                    [types.InlineKeyboardButton(text="📝 Обновить профиль", callback_data="update_profile")]
                ])
            
            await message.answer(
                f"👋 **Добро пожаловать обратно, {user['name']}!**\n\n"
                f"🔬 Дисциплина: {user['discipline']}\n"
                f"🏛️ Университет: {user['university']}\n\n"
                f"Выберите действие:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            # Новый пользователь - начинаем регистрацию
            await state.set_state(RegistrationStates.waiting_for_name)
            
            await message.answer(
                WELCOME_MESSAGE + 
                "\n\n**Как к Вам можно обращаться?**\n"
                "Пожалуйста, введите Ваше имя:",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Ошибка команды /start: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

# Обработка ввода имени
@dp.message(RegistrationStates.waiting_for_name)
async def handle_name_input(message: types.Message, state: FSMContext):
    """Обработка ввода имени"""
    try:
        name = message.text.strip()
        
        if len(name) < 2:
            await message.answer("❌ Имя должно содержать минимум 2 символа. Попробуйте еще раз:")
            return
        
        await state.update_data(name=name)
        await state.set_state(RegistrationStates.waiting_for_university)
        
        await message.answer(
            f"✅ Отлично, {name}!\n\n"
            "🏛️ **В каком университете Вы учитесь или работаете?**\n"
            "Укажите полное название университета:",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки имени: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте еще раз:")

# Обработка ввода университета
@dp.message(RegistrationStates.waiting_for_university)
async def handle_university_input(message: types.Message, state: FSMContext):
    """Обработка ввода университета"""
    try:
        university = message.text.strip()
        
        if len(university) < 3:
            await message.answer("❌ Название университета должно содержать минимум 3 символа. Попробуйте еще раз:")
            return
        
        await state.update_data(university=university)
        await state.set_state(RegistrationStates.waiting_for_discipline)
        
        # Создаем клавиатуру с дисциплинами
        keyboard = create_disciplines_keyboard()
        
        await message.answer(
            f"✅ Университет: {university}\n\n"
            "🔬 **Выберите Вашу научную дисциплину:**\n"
            "Это поможет нам подобрать подходящих коллег для междисциплинарных обсуждений.",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки университета: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте еще раз:")

# Обработка выбора дисциплины
@dp.callback_query(F.data.startswith("discipline_"))
async def handle_discipline_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора дисциплины"""
    try:
        discipline_id = int(callback.data.replace("discipline_", ""))
        discipline = SCIENTIFIC_DISCIPLINES[discipline_id]
        await state.update_data(discipline=discipline)
        await state.set_state(RegistrationStates.waiting_for_interests)
        
        await callback.message.edit_text(
            f"✅ Дисциплина: {discipline}\n\n"
            "🎯 **Опишите Ваши основные научные интересы:**\n"
            "Например: эпигенетика, ML в биологии, старение мозга, фармакология, биомаркеры, теломеры и т.д.\n\n"
            "Можете указать несколько интересов через запятую.",
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка выбора дисциплины: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте еще раз.")

# Обработка ввода интересов
@dp.message(RegistrationStates.waiting_for_interests)
async def handle_interests_input(message: types.Message, state: FSMContext):
    """Обработка ввода интересов"""
    try:
        interests = message.text.strip()
        
        if len(interests) < 5:
            await message.answer("❌ Пожалуйста, опишите ваши интересы более подробно (минимум 5 символов):")
            return
        
        await state.update_data(interests=interests)
        await state.set_state(RegistrationStates.waiting_for_education_level)
        
        # Создаем клавиатуру с уровнями образования
        keyboard = create_education_keyboard()
        
        await message.answer(
            f"✅ Интересы: {interests}\n\n"
            "🎓 **Укажите Ваш уровень образования:**",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки интересов: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте еще раз:")

# Обработка выбора уровня образования
@dp.callback_query(F.data.startswith("education_"))
async def handle_education_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора уровня образования"""
    try:
        education_id = int(callback.data.replace("education_", ""))
        education_level = EDUCATION_LEVELS[education_id]
        await state.update_data(education_level=education_level)
        await state.set_state(RegistrationStates.waiting_for_contact)
        
        await callback.message.edit_text(
            f"✅ Уровень образования: {education_level}\n\n"
            "📞 **Контактная информация (необязательно):**\n"
            "Можете указать дополнительную информацию для связи:\n"
            "• Email\n"
            "• Ссылку на профиль в LinkedIn\n"
            "• Другую контактную информацию\n\n"
            "Или просто напишите 'пропустить' для продолжения.",
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка выбора образования: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте еще раз.")

# Обработка ввода контактной информации
@dp.message(RegistrationStates.waiting_for_contact)
async def handle_contact_input(message: types.Message, state: FSMContext):
    """Обработка ввода контактной информации"""
    try:
        contact_info = message.text.strip()
        if contact_info.lower() in ['пропустить', 'skip', 'нет', 'no']:
            contact_info = ""
        
        await state.update_data(contact_info=contact_info)
        
        # Завершаем регистрацию
        data = await state.get_data()
        
        # Подготавливаем данные пользователя
        user_data = {
            'telegram_id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'name': data.get('name'),
            'university': data.get('university'),
            'discipline': data.get('discipline'),
            'interests': data.get('interests'),
            'education_level': data.get('education_level'),
            'contact_info': contact_info,
            'avatar_url': '',
            'telegram_profile': f"@{message.from_user.username}" if message.from_user.username else f"tg://user?id={message.from_user.id}"
        }
        
        # Сохраняем в базу данных
        success = db.add_user(user_data)
        
        if success:
            await state.clear()
            
            # Создаем клавиатуру в зависимости от прав пользователя
            if is_admin(message.from_user.id):
                # Администратор - полный доступ
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="🔍 Найти коллег", callback_data="find_colleagues")],
                    [types.InlineKeyboardButton(text="👥 Междисциплинарные команды", callback_data="interdisciplinary_teams")],
                    [types.InlineKeyboardButton(text="📊 Статистика сообщества", callback_data="community_stats")]
                ])
            else:
                # Обычный пользователь - ограниченный доступ
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="📊 Статистика сообщества", callback_data="community_stats")],
                    [types.InlineKeyboardButton(text="📝 Обновить профиль", callback_data="update_profile")]
                ])
            
            await message.answer(
                f"🎉 **Регистрация завершена успешно!**\n\n"
                f"📋 **Ваш профиль:**\n"
                f"🏛️ Университет: {data.get('university')}\n"
                f"🔬 Дисциплина: {data.get('discipline')}\n"
                f"🎯 Интересы: {data.get('interests')}\n"
                f"🎓 Уровень: {data.get('education_level')}\n\n"
                f"💬 **Контакт для связи:** {ADMIN_USERNAME}\n\n"
                f"Теперь вы можете искать коллег для междисциплинарных обсуждений!",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                "❌ Произошла ошибка при сохранении данных. "
                "Попробуйте зарегистрироваться заново командой /start"
            )
        
    except Exception as e:
        logger.error(f"Ошибка обработки контактов: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте еще раз:")

# Команда поиска (только для админов)
@dp.message(Command("find"))
async def find_command(message: types.Message):
    """Обработка команды поиска /find (только для админов)"""
    try:
        # Проверяем права администратора
        if not is_admin(message.from_user.id):
            await message.answer(
                "❌ **Доступ запрещен**\n\n"
                "Поиск специалистов доступен только администраторам.\n\n"
                "💡 **Доступные команды:**\n"
                "• `/start` - Начать работу с ботом\n"
                "• `/help` - Показать справку\n"
                "• `/stats` - Статистика сообщества\n\n"
                "💬 **Контакт для связи:** @SilentGene",
                parse_mode="Markdown"
            )
            return
        
        query = message.text.replace("/find", "").strip()
        
        if not query:
            await message.answer(
                "❌ Пожалуйста, укажите ключевые слова для поиска.\n"
                "Пример: `/find биоинформатика` или `/find эпигенетика`",
                parse_mode="Markdown"
            )
            return
        
        # Поиск в базе данных
        results = db.search_users(query, limit=20)
        
        if not results:
            await message.answer(
                f"🔍 **Поиск по запросу: '{query}'**\n\n"
                "❌ Участники с такими интересами не найдены.\n\n"
                "💡 **Попробуйте:**\n"
                "• Использовать другие ключевые слова\n"
                "• Поискать по дисциплине\n"
                "• Запросить междисциплинарный подбор"
            )
            return
        
        # Форматируем результаты (только для админов)
        response = f"🔍 **Результаты поиска: '{query}' - АДМИН-ПАНЕЛЬ**\n\n"
        response += f"Найдено участников: {len(results)}\n\n"
        
        for i, user in enumerate(results[:10], 1):  # Показываем первые 10
            response += f"**{i}. {user['name']}**\n"
            response += f"🏛️ {user['university']}\n"
            response += f"🔬 {user['discipline']}\n"
            response += f"🎯 {user['interests']}\n"
            response += f"🎓 {user['education_level']}\n"
            if user['telegram_profile']:
                response += f"📱 {user['telegram_profile']}\n"
            if user['contact_info']:
                response += f"📞 Контакты: {user['contact_info']}\n"
            response += "\n"
        
        if len(results) > 10:
            response += f"... и еще {len(results) - 10} участников\n"
        
        response += f"\n💬 **Контакт для связи:** {ADMIN_USERNAME}"
        
        await message.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Ошибка команды /find: {e}")
        await message.answer("❌ Произошла ошибка при поиске. Попробуйте позже.")

# Команда междисциплинарного подбора (только для админов)
@dp.message(Command("match"))
async def match_command(message: types.Message):
    """Обработка команды междисциплинарного подбора (только для админов)"""
    try:
        # Проверяем права администратора
        if not is_admin(message.from_user.id):
            await message.answer(
                "❌ **Доступ запрещен**\n\n"
                "Междисциплинарный подбор доступен только администраторам.\n\n"
                "💡 **Доступные команды:**\n"
                "• `/start` - Начать работу с ботом\n"
                "• `/help` - Показать справку\n"
                "• `/stats` - Статистика сообщества\n\n"
                "💬 **Контакт для связи:** @SilentGene",
                parse_mode="Markdown"
            )
            return
        
        if "interdisciplinary" in message.text.lower():
            # Получаем данные пользователя
            user = db.get_user(message.from_user.id)
            if not user:
                await message.answer(
                    "❌ Сначала необходимо зарегистрироваться командой /start"
                )
                return
            
            # Ищем совпадения
            matches = db.find_matches(user['id'], interdisciplinary=True)
            
            if not matches:
                await message.answer(
                    f"🔍 **Междисциплинарные совпадения для {user['name']}**\n\n"
                    "❌ Подходящие коллеги не найдены.\n\n"
                    "💡 **Попробуйте:**\n"
                    "• Обновить Ваши интересы\n"
                    "• Подождать новых участников\n"
                    "• Использовать поиск по ключевым словам"
                )
                return
            
            response = f"🔍 **Междисциплинарные совпадения для {user['name']} - АДМИН-ПАНЕЛЬ**\n\n"
            response += f"Найдено потенциальных коллег: {len(matches)}\n\n"
            
            for i, match in enumerate(matches[:10], 1):
                response += f"**{i}. {match['name']}**\n"
                response += f"🏛️ {match['university']}\n"
                response += f"🔬 {match['discipline']}\n"
                response += f"🎯 {match['interests']}\n"
                response += f"🎓 {match['education_level']}\n"
                if match['telegram_profile']:
                    response += f"📱 {match['telegram_profile']}\n"
                if match['contact_info']:
                    response += f"📞 Контакты: {match['contact_info']}\n"
                response += f"⭐ Совпадение: {match.get('match_score', 0):.1%}\n\n"
            
            if len(matches) > 10:
                response += f"... и еще {len(matches) - 10} участников\n"
            
            response += f"\n💬 **Контакт для связи:** {ADMIN_USERNAME}"
            
            await message.answer(response, parse_mode="Markdown")
        else:
            await message.answer(
                "❌ Неверная команда. Используйте:\n"
                "`/match interdisciplinary` - для междисциплинарного подбора",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Ошибка команды /match: {e}")
        await message.answer("❌ Произошла ошибка при поиске совпадений. Попробуйте позже.")

# Команда статистики
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    """Обработка команды статистики"""
    try:
        stats = db.get_statistics()
        
        if is_admin(message.from_user.id):
            # Администратор - полная статистика
            response = "📊 **Статистика научного сообщества (Админ-панель)**\n\n"
            response += f"👥 **Всего участников:** {stats.get('total_users', 0)}\n"
            response += f"🟢 **Активных за неделю:** {stats.get('active_users', 0)}\n\n"
            
            if stats.get('disciplines'):
                response += "🔬 **Участники по дисциплинам:**\n"
                for discipline, count in stats['disciplines'][:10]:  # Топ-10
                    response += f"• {discipline}: {count}\n"
                
                if len(stats['disciplines']) > 10:
                    response += f"... и еще {len(stats['disciplines']) - 10} дисциплин\n"
            
            response += f"\n💬 **Контакт для связи:** {ADMIN_USERNAME}"
        else:
            # Обычный пользователь - ограниченная статистика
            response = "📊 **Статистика научного сообщества**\n\n"
            response += f"👥 **Всего участников:** {stats.get('total_users', 0)}\n"
            response += f"🟢 **Активных за неделю:** {stats.get('active_users', 0)}\n\n"
            
            if stats.get('disciplines'):
                response += "🔬 **Участники по дисциплинам:**\n"
                for discipline, count in stats['disciplines'][:10]:  # Топ-10
                    response += f"• {discipline}: {count}\n"
                
                if len(stats['disciplines']) > 10:
                    response += f"... и еще {len(stats['disciplines']) - 10} дисциплин\n"
            
            response += f"\n💡 **Для поиска коллег обратитесь к администратору:** {ADMIN_USERNAME}"
        
        await message.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Ошибка команды /stats: {e}")
        await message.answer("❌ Произошла ошибка при получении статистики. Попробуйте позже.")

# Админ-команды
@dp.message(Command("list"))
async def list_command(message: types.Message):
    """Обработка команды списка участников (только для админов)"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ У Вас нет прав администратора.")
            return
        
        users = db.get_all_users()
        
        if not users:
            await message.answer("❌ Участники не найдены.")
            return
        
        response = f"👥 **Список всех участников ({len(users)}) - АДМИН-ПАНЕЛЬ**\n\n"
        
        for i, user in enumerate(users[:20], 1):  # Показываем первые 20
            response += f"**{i}. {user['name']}**\n"
            response += f"🏛️ {user['university']}\n"
            response += f"🔬 {user['discipline']}\n"
            response += f"🎯 {user['interests']}\n"
            response += f"🎓 {user['education_level']}\n"
            if user['telegram_profile']:
                response += f"📱 {user['telegram_profile']}\n"
            if user['contact_info']:
                response += f"📞 Контакты: {user['contact_info']}\n"
            response += f"📅 Регистрация: {user['registration_date']}\n\n"
        
        if len(users) > 20:
            response += f"... и еще {len(users) - 20} участников\n"
        
        response += f"\n💬 **Контакт для связи:** {ADMIN_USERNAME}"
        
        await message.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Ошибка команды /list: {e}")
        await message.answer("❌ Произошла ошибка при получении списка участников.")

# Команда экспорта
@dp.message(Command("export"))
async def export_command(message: types.Message):
    """Обработка команды экспорта (только для админов)"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ У вас нет прав администратора.")
            return
        
        # Получаем CSV данные
        csv_data = db.export_to_csv()
        
        if not csv_data:
            await message.answer("❌ Нет данных для экспорта.")
            return
        
        # Отправляем файл
        from io import BytesIO
        csv_file = BytesIO(csv_data.encode('utf-8'))
        csv_file.name = f"longevity_community_{message.date.strftime('%Y%m%d')}.csv"
        
        await message.answer_document(
            document=types.BufferedInputFile(
                file=csv_file.getvalue(),
                filename=csv_file.name
            ),
            caption="📤 **Экспорт данных сообщества**\n\n"
                   "Файл содержит информацию о всех зарегистрированных участниках."
        )
        
    except Exception as e:
        logger.error(f"Ошибка команды /export: {e}")
        await message.answer("❌ Произошла ошибка при экспорте данных.")

# Команда справки
@dp.message(Command("help"))
async def help_command(message: types.Message):
    """Обработка команды /help"""
    try:
        help_text = """
🔬 **Научное сообщество по продлению жизни**

**Основные команды:**
/start - Начать работу с ботом
/help - Показать эту справку
/find <ключевые слова> - Поиск участников по интересам
/match interdisciplinary - Междисциплинарные команды
/stats - Статистика сообщества

**Для администраторов:**
/list - Список всех участников
/export - Экспорт данных в CSV

**Цель проекта:**
Собрать сообщество молодых учёных и студентов из разных дисциплин
        """
        
        await message.answer(help_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Ошибка команды /help: {e}")
        await message.answer("❌ Произошла ошибка при показе справки.")

# Callback обработчики
@dp.callback_query(F.data == "find_colleagues")
async def find_colleagues_callback(callback: types.CallbackQuery):
    """Обработка поиска коллег"""
    # Проверяем права администратора
    if not is_admin(callback.from_user.id):
        await callback.message.edit_text(
            "❌ **Доступ запрещен**\n\n"
            "Поиск специалистов доступен только администраторам.\n\n"
            "💡 **Доступные команды:**\n"
            "• `/start` - Начать работу с ботом\n"
            "• `/help` - Показать справку\n"
            "• `/stats` - Статистика сообщества\n\n"
            "💬 **Контакт для связи:** @SilentGene",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🔍 **Поиск коллег**\n\n"
        "Используйте команду `/find <ключевые слова>` для поиска участников по интересам.\n\n"
        "Примеры:\n"
        "• `/find биоинформатика`\n"
        "• `/find эпигенетика`\n"
        "• `/find старение мозга`",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "interdisciplinary_teams")
async def interdisciplinary_teams_callback(callback: types.CallbackQuery):
    """Обработка междисциплинарных команд"""
    # Проверяем права администратора
    if not is_admin(callback.from_user.id):
        await callback.message.edit_text(
            "❌ **Доступ запрещен**\n\n"
            "Междисциплинарный подбор доступен только администраторам.\n\n"
            "💡 **Доступные команды:**\n"
            "• `/start` - Начать работу с ботом\n"
            "• `/help` - Показать справку\n"
            "• `/stats` - Статистика сообщества\n\n"
            "💬 **Контакт для связи:** @SilentGene",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "👥 **Междисциплинарные команды**\n\n"
        "Используйте команду `/match interdisciplinary` для поиска участников из других дисциплин для коллабораций.",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "community_stats")
async def community_stats_callback(callback: types.CallbackQuery):
    """Обработка статистики сообщества"""
    try:
        stats = db.get_statistics()
        
        if is_admin(callback.from_user.id):
            # Администратор - полная статистика
            response = "📊 **Статистика научного сообщества (Админ-панель)**\n\n"
            response += f"👥 **Всего участников:** {stats.get('total_users', 0)}\n"
            response += f"🟢 **Активных за неделю:** {stats.get('active_users', 0)}\n\n"
            
            if stats.get('disciplines'):
                response += "🔬 **Участники по дисциплинам:**\n"
                for discipline, count in stats['disciplines'][:10]:  # Топ-10
                    response += f"• {discipline}: {count}\n"
                
                if len(stats['disciplines']) > 10:
                    response += f"... и еще {len(stats['disciplines']) - 10} дисциплин\n"
            
            response += f"\n💬 **Контакт для связи:** {ADMIN_USERNAME}"
        else:
            # Обычный пользователь - ограниченная статистика
            response = "📊 **Статистика научного сообщества**\n\n"
            response += f"👥 **Всего участников:** {stats.get('total_users', 0)}\n"
            response += f"🟢 **Активных за неделю:** {stats.get('active_users', 0)}\n\n"
            
            if stats.get('disciplines'):
                response += "🔬 **Участники по дисциплинам:**\n"
                for discipline, count in stats['disciplines'][:10]:  # Топ-10
                    response += f"• {discipline}: {count}\n"
                
                if len(stats['disciplines']) > 10:
                    response += f"... и еще {len(stats['disciplines']) - 10} дисциплин\n"
            
            response += f"\n💡 **Для поиска коллег обратитесь к администратору:** {ADMIN_USERNAME}"
        
        await callback.message.edit_text(response, parse_mode="Markdown")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка callback статистики: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при получении статистики.")
        await callback.answer()

@dp.callback_query(F.data == "update_profile")
async def update_profile_callback(callback: types.CallbackQuery):
    """Обработка обновления профиля"""
    await callback.message.edit_text(
        "📝 **Обновление профиля**\n\n"
        "Для обновления профиля используйте команду `/start` и пройдите регистрацию заново.\n\n"
        "💡 **Доступные команды:**\n"
        "• `/start` - Начать работу с ботом\n"
        "• `/help` - Показать справку\n"
        "• `/stats` - Статистика сообщества\n\n"
        "💬 **Контакт для связи:** @SilentGene",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "recommendations")
async def recommendations_callback(callback: types.CallbackQuery):
    """Обработка рекомендаций"""
    # Проверяем права администратора
    if not is_admin(callback.from_user.id):
        await callback.message.edit_text(
            "❌ **Доступ запрещен**\n\n"
            "Персональные рекомендации доступны только администраторам.\n\n"
            "💡 **Доступные команды:**\n"
            "• `/start` - Начать работу с ботом\n"
            "• `/help` - Показать справку\n"
            "• `/stats` - Статистика сообщества\n\n"
            "💬 **Контакт для связи:** @SilentGene",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🎯 **Рекомендации**\n\n"
        "Используйте команду `/match interdisciplinary` для получения персональных рекомендаций коллег.",
        parse_mode="Markdown"
    )
    await callback.answer()

# Вспомогательные функции
def create_disciplines_keyboard() -> types.InlineKeyboardMarkup:
    """Создание клавиатуры с дисциплинами"""
    keyboard = []
    
    # Разбиваем дисциплины на группы по 2
    for i in range(0, len(SCIENTIFIC_DISCIPLINES), 2):
        row = []
        for j in range(2):
            if i + j < len(SCIENTIFIC_DISCIPLINES):
                discipline = SCIENTIFIC_DISCIPLINES[i + j]
                # Используем индекс вместо полного названия для callback_data
                discipline_id = i + j
                row.append(types.InlineKeyboardButton(
                    text=discipline,
                    callback_data=f"discipline_{discipline_id}"
                ))
        keyboard.append(row)
    
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_education_keyboard() -> types.InlineKeyboardMarkup:
    """Создание клавиатуры с уровнями образования"""
    keyboard = []
    
    # Разбиваем уровни образования на группы по 2
    for i in range(0, len(EDUCATION_LEVELS), 2):
        row = []
        for j in range(2):
            if i + j < len(EDUCATION_LEVELS):
                level = EDUCATION_LEVELS[i + j]
                # Используем индекс вместо полного названия для callback_data
                level_id = i + j
                row.append(types.InlineKeyboardButton(
                    text=level,
                    callback_data=f"education_{level_id}"
                ))
        keyboard.append(row)
    
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

# Основная функция запуска бота
async def main():
    """Основная функция запуска бота"""
    try:
        logger.info("Запуск бота научного сообщества...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
