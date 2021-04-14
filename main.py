from data import db_session
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from data.books import Books
from data.users import User
from telegram import ReplyKeyboardMarkup

TOKEN = 'google'

# All KeyBoards -------------------------------------------------------------------------------------------

main_keyboard = [['Мои книги']]
main_markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=False)

library_keyboard = [['Добавить книгу', 'Удалить книгу'],
                    ['Меню']]
library_markup = ReplyKeyboardMarkup(library_keyboard, one_time_keyboard=False)

just_menu_keyboard = [['Меню']]
just_menu_markup = ReplyKeyboardMarkup(just_menu_keyboard, one_time_keyboard=False)


# ----------------------------------------------------------------------------------------------------------
# Adding to DataBase


def start(update, context):
    db_ses = db_session.create_session()
    user = User()
    user.id = update.effective_user.id
    user.username = update.effective_user.username
    user.first_name = update.effective_user.first_name
    if not db_ses.query(User).filter(User.id == user.id).all():
        db_ses.add(user)
    db_ses.commit()
    update.message.reply_text('Приветствую, ' + update.effective_user.first_name + '. Я - бот, который поможет '
                                                                                   'тебя усовершенствоваться в '
                                                                                   'саморазвитии, самоорганизации, '
                                                                                   'самоконтроле. Поверь, '
                                                                                   'тебе это очень сильго поможет '
                                                                                   'в жизни', reply_markup=main_markup)


# Returns user to main menu -----------------------------------------------------------------------------------------


def back_to_menu(update, context):
    update.message.reply_text('Вы вернулись в меню',
                              reply_markup=main_markup)


# --------------------------------------------------------------------------------------------------------------------
# Showing All User Books


def library(update, context):
    db_ses = db_session.create_session()
    user = db_ses.query(User).filter(User.id == update.effective_user.id).first()
    if db_ses.query(Books).filter(Books.user == user).all():
        update.message.reply_text('Ваши книги:', reply_markup=library_markup)
        for i in db_ses.query(Books).filter(Books.user == user):
            update.message.reply_text(str(i.id) + ' ' + i.title, reply_markup=library_markup)
    else:
        name = user.first_name
        update.message.reply_text(name + ', ' + 'У вас пока нет книг...', reply_markup=library_markup)
    return 1


# Library commands


def library_commands(update, context):
    if update.message.text == 'Добавить книгу':
        update.message.reply_text('Пожалуйста введите название книги',
                                  reply_markup=just_menu_markup)
        return 2
    elif update.message.text == 'Удалить книгу':
        db_ses = db_session.create_session()
        user = db_ses.query(User).filter(User.id == update.effective_user.id).first()
        if user.books:
            message = '\n'.join(str(t.id) + ' ' + t.title for t in user.books)
            update.message.reply_text(message,
                                      reply_markup=ReplyKeyboardMarkup(
                                          [[i.id for i in user.books[:len(list(user.books)) // 2]],
                                           [i.id for i in user.books[len(list(user.books)) // 2:]],
                                           ['Меню']], one_time_keyboard=False))
            return 3
        else:
            name = user.first_name
            update.message.reply_text(name + ', ' + 'У вас пока нет книг...', reply_markup=library_markup)
            return 1
    elif update.message.text == 'Меню':
        back_to_menu(update, context)
        return ConversationHandler.END
    else:
        unknown_message(update, context)
        return ConversationHandler.END


# Adding books


def add_book(update, context):
    if update.message.text == 'Меню':
        back_to_menu(update, context)
        return ConversationHandler.END
    db_ses = db_session.create_session()
    user = db_ses.query(User).filter(User.id == update.effective_user.id).first()
    book = Books()
    book.title = update.message.text
    if book.title not in [i.title for i in user.books]:
        user.books.append(book)
        db_ses.commit()
        update.message.reply_text('Книга успешно добавлена', reply_markup=library_markup)
        return 1
    else:
        update.message.reply_text('У Вас уже есть эта книга', reply_markup=library_markup)
        return 1


# Deleting Books


def delete_book(update, context):
    if update.message.text == 'Меню':
        back_to_menu(update, context)
        return ConversationHandler.END
    db_ses = db_session.create_session()
    book = db_ses.query(Books).filter(Books.id == update.message.text).first()
    db_ses.delete(book)
    db_ses.commit()
    update.message.reply_text('Книга успешно удалена', reply_markup=library_markup)
    return 1


# Unknown message


def unknown_message(update, context):
    update.message.reply_text('Извините, я не понимаю Вас...',
                              reply_markup=main_markup)


def main():
    db_session.global_init('db/main.db')
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Мои книги'), library)],
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.text, library_commands)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(Filters.text, add_book)],
            3: [MessageHandler(Filters.text, delete_book)]
        },

        fallbacks=[MessageHandler(Filters.text, unknown_message)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text, unknown_message))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
