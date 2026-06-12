import logging
import os
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ===== CONFIG =====
BOT_TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "PASTE_YOUR_CHAT_ID_HERE")

# ===== CONVERSATION STATES =====
(
    CONTENT_TYPE,
    PLATFORM,
    HAS_SCRIPT,
    MONTHLY_VOLUME,
    BUDGET,
    EXAMPLES,
    DEADLINE,
    NAME_CONTACT,
) = range(8)

QUESTIONS = {
    CONTENT_TYPE: "1️⃣ Який тип контенту вам потрібен?\n(UGC реклама / контент для блогу / монтаж довгих відео / інше)",
    PLATFORM: "2️⃣ Для якої платформи і формату?\n(TikTok / Instagram Reels / YouTube Shorts / горизонтальний YouTube)",
    HAS_SCRIPT: "3️⃣ У вас вже є сценарій або готовий матеріал, чи потрібна допомога з ідеєю та сценарієм?",
    MONTHLY_VOLUME: "4️⃣ Скільки відео плануєте на місяць?\n(орієнтовно — разово, або постійна співпраця)",
    BUDGET: "5️⃣ Який у вас орієнтовний бюджет на одне відео?",
    EXAMPLES: "6️⃣ Чи є приклади відео в стилі, який вам подобається?\n(можна надіслати посилання на TikTok/Instagram/YouTube)",
    DEADLINE: "7️⃣ Який дедлайн на перше відео?",
    NAME_CONTACT: "8️⃣ І останнє — як до вас звертатись, та який кращий контакт для зв'язку (Telegram / email)?",
}

FIELD_LABELS = {
    CONTENT_TYPE: "Тип контенту",
    PLATFORM: "Платформа / формат",
    HAS_SCRIPT: "Сценарій / матеріал",
    MONTHLY_VOLUME: "Обсяг на місяць",
    BUDGET: "Бюджет за відео",
    EXAMPLES: "Референси",
    DEADLINE: "Дедлайн",
    NAME_CONTACT: "Ім'я та контакт",
}

ORDER = [
    CONTENT_TYPE,
    PLATFORM,
    HAS_SCRIPT,
    MONTHLY_VOLUME,
    BUDGET,
    EXAMPLES,
    DEADLINE,
    NAME_CONTACT,
]

# ===== PORTFOLIO =====
PORTFOLIO_ITEMS = [
    (
        "🏆 Sport UGC",
        "Динамічний монтаж спортивного контенту — ритм, акценти, енергія",
        "https://drive.google.com/file/d/13ul_ytQM9QWm465H4zFCYC_OCh6mOWXu/view",
    ),
    (
        "🎬 UGC Content Creator Edit",
        "Реклама у форматі creator-style — природно, але продає",
        "https://drive.google.com/file/d/19p5W9RN3VLA7vpOKv9rT2ZIui9TyeyDw/view",
    ),
    (
        "✨ AI-анімація",
        "Креативний монтаж з генеративним відео та анімацією",
        "https://drive.google.com/file/d/1NoTy-5WBAbw4Wys3DhDq7s-kcUg5qX_9/view",
    ),
    (
        "🎙️ Podcast Reels",
        "Нарізки подкасту під формат соцмереж — субтитри, акценти, динаміка",
        "https://drive.google.com/file/d/1Aqe2ninFoqIVtbM3LfzK1yyjm1RBBGva/view",
    ),
    (
        "🎯 Targeted Ad Reel",
        "Рекламний ролик під таргетинг — чіткий хук і структура",
        "https://drive.google.com/file/d/1Uc1hOZBlkzYcRpWo8rkqsQWmm5YZ-NQa/view",
    ),
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "👋 <b>Привіт! Я асистент BonitoVisual</b> 🎬\n\n"
        "Монтую UGC/рекламні відео для брендів — TikTok, Reels, "
        "YouTube Shorts. Допоможу швидко зібрати інформацію про ваш проєкт, "
        "щоб запропонувати найкраще рішення.\n\n"
        "📂 Хочете спочатку подивитись приклади робіт? Напишіть /portfolio\n\n"
        "Це опитування займе ~2 хвилини. Почнемо? 🚀\n\n"
        + QUESTIONS[CONTENT_TYPE],
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    return CONTENT_TYPE


async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = ["🎥 <b>Приклади робіт BonitoVisual</b>\n"]
    for title, desc, url in PORTFOLIO_ITEMS:
        lines.append(f"<b>{title}</b>\n{desc}\n{url}\n")
    lines.append("Сподобався стиль? Напишіть /start щоб обговорити ваш проєкт 👇")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


def make_handler(current_state: int, next_state: int):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data[current_state] = update.message.text
        await update.message.reply_text(QUESTIONS[next_state])
        return next_state

    return handler


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data[NAME_CONTACT] = update.message.text

    user = update.effective_user
    summary_lines = [
        "📋 <b>Новий бриф від клієнта</b> 🔥",
        f"👤 Telegram: @{user.username}" if user.username else f"👤 Telegram ID: {user.id}",
        "",
    ]
    for state in ORDER:
        answer = context.user_data.get(state, "—")
        summary_lines.append(f"<b>{FIELD_LABELS[state]}:</b> {answer}")

    summary_text = "\n".join(summary_lines)

    # Send the summary to the admin (you)
    if ADMIN_CHAT_ID and ADMIN_CHAT_ID != "PASTE_YOUR_CHAT_ID_HERE":
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=summary_text,
            parse_mode="HTML",
        )

    await update.message.reply_text(
        "Дякую! ✅🎬\n\n"
        "Ваші відповіді отримано. Я переглядаю заявки особисто і відповідаю "
        "протягом кількох годин з варіантами та орієнтовною ціною.\n\n"
        "До зв'язку! 🚀"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Опитування скасовано. Якщо захочете почати знову — введіть /start.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Build the chain of states: each state moves to the next on text input
    states = {}
    for i, state in enumerate(ORDER):
        if state == NAME_CONTACT:
            states[state] = [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)]
        else:
            next_state = ORDER[i + 1]
            states[state] = [
                MessageHandler(filters.TEXT & ~filters.COMMAND, make_handler(state, next_state))
            ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states=states,
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("portfolio", portfolio))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
