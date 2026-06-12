import logging
import os
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
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
    ENTRY,
    CONTENT_TYPE,
    PLATFORM,
    HAS_SCRIPT,
    MONTHLY_VOLUME,
    BUDGET,
    EXAMPLES,
    DEADLINE,
    EXTRA_NOTES,
) = range(9)

QUESTIONS = {
    CONTENT_TYPE: "1\u20e3 \u042f\u043a\u0438\u0439 \u0442\u0438\u043f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0443 \u0432\u0430\u043c \u043f\u043e\u0442\u0440\u0456\u0431\u0435\u043d?\n(UGC \u0440\u0435\u043a\u043b\u0430\u043c\u0430 / \u043a\u043e\u043d\u0442\u0435\u043d\u0442 \u0434\u043b\u044f \u0431\u043b\u043e\u0433\u0443 / \u043c\u043e\u043d\u0442\u0430\u0436 \u0434\u043e\u0432\u0433\u0438\u0445 \u0432\u0456\u0434\u0435\u043e / \u0456\u043d\u0448\u0435)",
    PLATFORM: "2\u20e3 \u0414\u043b\u044f \u044f\u043a\u043e\u0457 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0438 \u0456 \u0444\u043e\u0440\u043c\u0430\u0442\u0443?\n(TikTok / Instagram Reels / YouTube Shorts / \u0433\u043e\u0440\u0438\u0437\u043e\u043d\u0442\u0430\u043b\u044c\u043d\u0438\u0439 YouTube)",
    HAS_SCRIPT: "3\u20e3 \u0423 \u0432\u0430\u0441 \u0432\u0436\u0435 \u0454 \u0441\u0446\u0435\u043d\u0430\u0440\u0456\u0439 \u0430\u0431\u043e \u0433\u043e\u0442\u043e\u0432\u0438\u0439 \u043c\u0430\u0442\u0435\u0440\u0456\u0430\u043b, \u0447\u0438 \u043f\u043e\u0442\u0440\u0456\u0431\u043d\u0430 \u0434\u043e\u043f\u043e\u043c\u043e\u0433\u0430 \u0437 \u0456\u0434\u0435\u0454\u044e \u0442\u0430 \u0441\u0446\u0435\u043d\u0430\u0440\u0456\u0454\u043c?",
    MONTHLY_VOLUME: "4\u20e3 \u0421\u043a\u0456\u043b\u044c\u043a\u0438 \u0432\u0456\u0434\u0435\u043e \u043f\u043b\u0430\u043d\u0443\u0454\u0442\u0435 \u043d\u0430 \u043c\u0456\u0441\u044f\u0446\u044c?\n(\u043e\u0440\u0456\u0454\u043d\u0442\u043e\u0432\u043d\u043e \u2014 \u0440\u0430\u0437\u043e\u0432\u043e, \u0430\u0431\u043e \u043f\u043e\u0441\u0442\u0456\u0439\u043d\u0430 \u0441\u043f\u0456\u0432\u043f\u0440\u0430\u0446\u044f)",
    BUDGET: "5\u20e3 \u042f\u043a\u0438\u0439 \u0443 \u0432\u0430\u0441 \u043e\u0440\u0456\u0454\u043d\u0442\u043e\u0432\u043d\u0438\u0439 \u0431\u044e\u0434\u0436\u0435\u0442 \u043d\u0430 \u043e\u0434\u043d\u0435 \u0432\u0456\u0434\u0435\u043e?",
    EXAMPLES: "6\u20e3 \u0427\u0438 \u0454 \u043f\u0440\u0438\u043a\u043b\u0430\u0434\u0438 \u0432\u0456\u0434\u0435\u043e \u0432 \u0441\u0442\u0438\u043b\u0456, \u044f\u043a\u0438\u0439 \u0432\u0430\u043c \u043f\u043e\u0434\u043e\u0431\u0430\u0454\u0442\u044c\u0441\u044f?\n(\u043c\u043e\u0436\u043d\u0430 \u043d\u0430\u0434\u0456\u0441\u043b\u0430\u0442\u0438 \u043f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 TikTok/Instagram/YouTube)",
    DEADLINE: "7\u20e3 \u042f\u043a\u0438\u0439 \u0434\u0435\u0434\u043b\u0430\u0439\u043d \u043d\u0430 \u043f\u0435\u0440\u0448\u0435 \u0432\u0456\u0434\u0435\u043e?",
    EXTRA_NOTES: "8\u20e3 \u041e\u0441\u0442\u0430\u043d\u043d\u0454: \u0447\u0438 \u0454 \u0434\u043e\u0434\u0430\u0442\u043a\u043e\u0432\u0456 \u0434\u0435\u0442\u0430\u043b\u0456 \u0430\u0431\u043e \u043f\u043e\u0436\u0435\u043b\u0430\u043d\u043d\u044f \u0449\u043e\u0434\u043e \u043f\u0440\u043e\u0454\u043a\u0442\u0443?\n(\u044f\u043a\u0449\u043e \u043d\u0456\u0447\u043e\u0433\u043e \u0434\u043e\u0434\u0430\u0442\u0438 \u2014 \u043f\u0440\u043e\u0441\u0442\u043e \u043d\u0430\u043f\u0438\u0448\u0456\u0442\u044c \u00ab\u043d\u0435\u043c\u0430\u0454\u00bb)",
}

FIELD_LABELS = {
    CONTENT_TYPE: "\u0422\u0438\u043f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0443",
    PLATFORM: "\u041f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0430 / \u0444\u043e\u0440\u043c\u0430\u0442",
    HAS_SCRIPT: "\u0421\u0446\u0435\u043d\u0430\u0440\u0456\u0439 / \u043c\u0430\u0442\u0435\u0440\u0456\u0430\u043b",
    MONTHLY_VOLUME: "\u041e\u0431\u0441\u044f\u0433 \u043d\u0430 \u043c\u0456\u0441\u044f\u0446\u044c",
    BUDGET: "\u0411\u044e\u0434\u0436\u0435\u0442 \u0437\u0430 \u0432\u0456\u0434\u0435\u043e",
    EXAMPLES: "\u0420\u0435\u0444\u0435\u0440\u0435\u043d\u0441\u0438",
    DEADLINE: "\u0414\u0435\u0434\u043b\u0430\u0439\u043d",
    EXTRA_NOTES: "\u0414\u043e\u0434\u0430\u0442\u043a\u043e\u0432\u0456 \u0434\u0435\u0442\u0430\u043b\u0456",
}

ORDER = [
    CONTENT_TYPE,
    PLATFORM,
    HAS_SCRIPT,
    MONTHLY_VOLUME,
    BUDGET,
    EXAMPLES,
    DEADLINE,
    EXTRA_NOTES,
]

# ===== PORTFOLIO =====
PORTFOLIO_ITEMS = [
    (
        "\U0001f3c6 Sport UGC",
        "\u0414\u0438\u043d\u0430\u043c\u0456\u0447\u043d\u0438\u0439 \u043c\u043e\u043d\u0442\u0430\u0436 \u0441\u043f\u043e\u0440\u0442\u0438\u0432\u043d\u043e\u0433\u043e \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0443 \u2014 \u0440\u0438\u0442\u043c, \u0430\u043a\u0446\u0435\u043d\u0442\u0438, \u0435\u043d\u0435\u0440\u0433\u0456\u044f",
        "https://drive.google.com/file/d/13ul_ytQM9QWm465H4zFCYC_OCh6mOWXu/view",
    ),
    (
        "\U0001f3ac UGC Content Creator Edit",
        "\u0420\u0435\u043a\u043b\u0430\u043c\u0430 \u0443 \u0444\u043e\u0440\u043c\u0430\u0442\u0456 creator-style \u2014 \u043f\u0440\u0438\u0440\u043e\u0434\u043d\u043e, \u0430\u043b\u0435 \u043f\u0440\u043e\u0434\u0430\u0454",
        "https://drive.google.com/file/d/19p5W9RN3VLA7vpOKv9rT2ZIui9TyeyDw/view",
    ),
    (
        "\u2728 AI-\u0430\u043d\u0456\u043c\u0430\u0446\u0456\u044f",
        "\u041a\u0440\u0435\u0430\u0442\u0438\u0432\u043d\u0438\u0439 \u043c\u043e\u043d\u0442\u0430\u0436 \u0437 \u0433\u0435\u043d\u0435\u0440\u0430\u0442\u0438\u0432\u043d\u0438\u043c \u0432\u0456\u0434\u0435\u043e \u0442\u0430 \u0430\u043d\u0456\u043c\u0430\u0446\u0456\u0454\u044e",
        "https://drive.google.com/file/d/1NoTy-5WBAbw4Wys3DhDq7s-kcUg5qX_9/view",
    ),
    (
        "\U0001f399\ufe0f Podcast Reels",
        "\u041d\u0430\u0440\u0456\u0437\u043a\u0438 \u043f\u043e\u0434\u043a\u0430\u0441\u0442\u0443 \u043f\u0456\u0434 \u0444\u043e\u0440\u043c\u0430\u0442 \u0441\u043e\u0446\u043c\u0435\u0440\u0435\u0436 \u2014 \u0441\u0443\u0431\u0442\u0438\u0442\u0440\u0438, \u0430\u043a\u0446\u0435\u043d\u0442\u0438, \u0434\u0438\u043d\u0430\u043c\u0456\u043a\u0430",
        "https://drive.google.com/file/d/1Aqe2ninFoqIVtbM3LfzK1yyjm1RBBGva/view",
    ),
    (
        "\U0001f3af Targeted Ad Reel",
        "\u0420\u0435\u043a\u043b\u0430\u043c\u043d\u0438\u0439 \u0440\u043e\u043b\u0438\u043a \u043f\u0456\u0434 \u0442\u0430\u0440\u0433\u0435\u0442\u0438\u043d\u0433 \u2014 \u0447\u0456\u0442\u043a\u0438\u0439 \u0445\u0443\u043a \u0456 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430",
        "https://drive.google.com/file/d/1Uc1hOZBlkzYcRpWo8rkqsQWmm5YZ-NQa/view",
    ),
]

BEGIN_KEYBOARD = InlineKeyboardMarkup(
    [[InlineKeyboardButton("\U0001f680 \u041f\u043e\u0447\u0430\u0442\u0438 \u043e\u043f\u0438\u0442\u0443\u0432\u0430\u043d\u043d\u044f", callback_data="begin_survey")]]
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "\u2728 <b>BonitoVisual</b> \u2728\n"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
        "\U0001f44b \u041f\u0440\u0438\u0432\u0456\u0442! \u042f \u0430\u0441\u0438\u0441\u0442\u0435\u043d\u0442 <b>BonitoVisual</b> \U0001f3ac\n\n"
        "\u041c\u043e\u043d\u0442\u0443\u044e UGC / \u0440\u0435\u043a\u043b\u0430\u043c\u043d\u0456 \u0432\u0456\u0434\u0435\u043e \u0434\u043b\u044f \u0431\u0440\u0435\u043d\u0434\u0456\u0432 \u2014 TikTok, Instagram Reels, "
        "YouTube Shorts. \u0411\u0438\u0441\u0442\u0440\u043e, \u0437 \u0430\u043a\u0446\u0435\u043d\u0442\u043e\u043c \u043d\u0430 \u0440\u0438\u0442\u043c, \u0443\u0442\u0440\u0438\u043c\u0430\u043d\u043d\u044f \u0443\u0432\u0430\u0433\u0438 \u0456 \u043a\u043e\u043d\u0432\u0435\u0440\u0441\u0456\u044e.\n\n"
        "\U0001f4c2 \u041f\u0440\u0438\u043a\u043b\u0430\u0434\u0438 \u0440\u043e\u0431\u0456\u0442: /portfolio\n\n"
        "\u041d\u0430\u0442\u0438\u0441\u043d\u0456\u0442\u044c \u043a\u043d\u043e\u043f\u043a\u0443 \u043d\u0438\u0436\u0447\u0435, \u0449\u043e\u0431 \u0440\u043e\u0437\u043f\u043e\u0432\u0456\u0441\u0442\u0438 \u043f\u0440\u043e \u0432\u0430\u0448 \u043f\u0440\u043e\u0454\u043a\u0442 \u2014 "
        "\u0446\u0435 \u0437\u0430\u0439\u043c\u0435 ~2 \u0445\u0432\u0438\u043b\u0438\u043d\u0438, \u0456 \u044f \u043f\u043e\u0432\u0435\u0440\u043d\u0443\u0441\u044c \u0437 \u043f\u0440\u043e\u043f\u043e\u0437\u0438\u0446\u0456\u0454\u044e \u0442\u0430 \u043e\u0440\u0456\u0454\u043d\u0442\u043e\u0432\u043d\u043e\u044e \u0446\u0456\u043d\u043e\u044e. \U0001f447",
        reply_markup=BEGIN_KEYBOARD,
        parse_mode="HTML",
    )
    return ENTRY


async def begin_survey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=QUESTIONS[CONTENT_TYPE],
    )
    return CONTENT_TYPE


async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = ["\U0001f3a5 <b>\u041f\u0440\u0438\u043a\u043b\u0430\u0434\u0438 \u0440\u043e\u0431\u0456\u0442 BonitoVisual</b>\n"]
    for title, desc, url in PORTFOLIO_ITEMS:
        lines.append(f"<b>{title}</b>\n{desc}\n{url}\n")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    await update.message.reply_text(
        "\u0421\u043f\u043e\u0434\u043e\u0431\u0430\u0432\u0441\u044f \u0441\u0442\u0438\u043b\u044c? \u041d\u0430\u0442\u0438\u0441\u043d\u0456\u0442\u044c \u043a\u043d\u043e\u043f\u043a\u0443, \u0449\u043e\u0431 \u043e\u0431\u0433\u043e\u0432\u043e\u0440\u0438\u0442\u0438 \u0432\u0430\u0448 \u043f\u0440\u043e\u0454\u043a\u0442 \U0001f447",
        reply_markup=BEGIN_KEYBOARD,
    )


def make_handler(current_state: int, next_state: int):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data[current_state] = update.message.text
        await update.message.reply_text(QUESTIONS[next_state])
        return next_state

    return handler


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data[EXTRA_NOTES] = update.message.text

    user = update.effective_user
    contact = f"@{user.username}" if user.username else f"ID {user.id}"

    summary_lines = [
        "\U0001f4cb <b>\u041d\u043e\u0432\u0438\u0439 \u0431\u0440\u0438\u0444 \u0432\u0456\u0434 \u043a\u043b\u0456\u0454\u043d\u0442\u0430</b> \U0001f525",
        f"\U0001f464 \u041a\u043e\u043d\u0442\u0430\u043a\u0442: {contact}",
        "",
    ]
    for state in ORDER:
        answer = context.user_data.get(state, "\u2014")
        summary_lines.append(f"<b>{FIELD_LABELS[state]}:</b> {answer}")

    summary_text = "\n".join(summary_lines)

    if ADMIN_CHAT_ID and ADMIN_CHAT_ID != "PASTE_YOUR_CHAT_ID_HERE":
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=summary_text,
            parse_mode="HTML",
        )

    await update.message.reply_text(
        "\u0414\u044f\u043a\u0443\u044e! \u2705\U0001f3ac\n\n"
        "\u0412\u0430\u0448\u0456 \u0432\u0456\u0434\u043f\u043e\u0432\u0456\u0434\u0456 \u043e\u0442\u0440\u0438\u043c\u0430\u043d\u043e. \u042f \u043f\u0435\u0440\u0435\u0433\u043b\u044f\u0434\u0430\u044e \u0437\u0430\u044f\u0432\u043a\u0438 \u043e\u0441\u043e\u0431\u0438\u0441\u0442\u043e \u0456 \u0432\u0456\u0434\u043f\u043e\u0432\u0456\u0434\u0430\u044e "
        "\u043f\u0440\u043e\u0442\u044f\u0433\u043e\u043c \u043a\u0456\u043b\u044c\u043a\u043e\u0445 \u0433\u043e\u0434\u0438\u043d \u0437 \u0432\u0430\u0440\u0456\u0430\u043d\u0442\u0430\u043c\u0438 \u0442\u0430 \u043e\u0440\u0456\u0454\u043d\u0442\u043e\u0432\u043d\u043e\u044e \u0446\u0456\u043d\u043e\u044e.\n\n"
        "\u0414\u043e \u0437\u0432'\u044f\u0437\u043a\u0443! \U0001f680",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "\u041e\u043f\u0438\u0442\u0443\u0432\u0430\u043d\u043d\u044f \u0441\u043a\u0430\u0441\u043e\u0432\u0430\u043d\u043e. \u042f\u043a\u0449\u043e \u0437\u0430\u0445\u043e\u0447\u0435\u0442\u0435 \u043f\u043e\u0447\u0430\u0442\u0438 \u0437\u043d\u043e\u0432\u0443 \u2014 \u0432\u0432\u0435\u0434\u0438\u0442\u044c /start.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    states = {
        ENTRY: [CallbackQueryHandler(begin_survey, pattern="^begin_survey$")],
    }
    for i, state in enumerate(ORDER):
        if state == EXTRA_NOTES:
            states[state] = [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)]
        else:
            next_state = ORDER[i + 1]
            states[state] = [
                MessageHandler(filters.TEXT & ~filters.COMMAND, make_handler(state, next_state))
            ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states=states,
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("portfolio", portfolio))
    application.add_handler(CallbackQueryHandler(begin_survey, pattern="^begin_survey$"))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
