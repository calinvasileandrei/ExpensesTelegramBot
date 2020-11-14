#telegram imports
from telegram import Update,ReplyKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    Filters,
    ConversationHandler,
    CallbackContext)
#other imports
import os
from src.main.utils.base_logger import logger
#my imports
import src.main.database.db_manager as myDbManager

CHOOSING, NEW_REPLY, TYPING_CHOICE, DELETE_REPLY, UPDATE_REPLY, UPDATE_CHOOSING, UPDATE_MOFIFY = range(7)
reply_keyboard = [
    ['New expense', 'Show expenses'],
    ['Delete expense', 'Update expense'],
    ['Done'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    #Send a message when the command /start is issued.
    try:
        myDbManager.newUser(update.message.from_user)    
    except:
        logger.info("error validating the user!")
    try:
        update.message.reply_text(
            "Hi Im Expenses and I ll help you to track your expenses :) ",
            reply_markup=markup
    )
    except TelegramError as e:
        logger.error(e)

    return CHOOSING

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data

    update.message.reply_text(
        "Bye Bye! :)"
    )

    user_data.clear()
    return ConversationHandler.END

#DB METHODS

#create a new expense typing name , price and date
def new_expense_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Type the expense:\n NAME, PRICE, DATE\n (dd/mm/yyyy or leave it blank for today):'
    )

    return NEW_REPLY

def new_expense_reply(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logger.info("text:"+str(text))
    logger.info("id:"+str(update.message.from_user.id))
    event = myDbManager.createExpense(update.message.from_user.id,text)

    update.message.reply_text(
        "Nice the following expense has been created:\n"+str(event),
        reply_markup=markup,
    )

    return CHOOSING


#show to the user all the expenses
def show_expenses_choice(update: Update, context: CallbackContext) -> int:
    list_expenses = myDbManager.getExpenses(update.message.from_user.id)
    update.message.reply_text(
        "Your expenses are:\n"+list_expenses if (len(list_expenses)>0) else "No expenses founded!",
        reply_markup=markup
    )

    return CHOOSING



#Delete expense by providing the list to the user of all the expenses , than the user type the one to delete
def delete_expense_choice(update: Update, context: CallbackContext) -> int:
    list_expenses = myDbManager.getExpensesSelectable(update.message.from_user.id)
    logger.info("ls:"+str(list_expenses))
    message=""
    response_list= []
    for ex in list_expenses:
        response_list.append(str(ex["id"]))
        message += str(ex["id"])+ ") "+str(ex["date"])+"| "+str(ex["name"])+" - "+str(ex["price"])+"€\n\n"

    markup_ids = ReplyKeyboardMarkup(response_list, one_time_keyboard=True)

    update.message.reply_text(
        "Your expenses are:\n"+message,
        reply_markup=markup_ids
    )
    context.user_data['list_expenses'] = list_expenses



    return DELETE_REPLY

#Recive the user input of the expense to delete and procede with the delete from the db
def delete_expense_replay(update: Update, context: CallbackContext) -> int:
    selected = update.message.text
    list_expenses = context.user_data["list_expenses"]

    #get the object id from given a numeric id
    oid_selected = [item for item in list_expenses if str(item["id"]) == str(selected)][0]

    #calling the delete method
    myDbManager.deleteExpense(update.message.from_user.id,oid_selected["_id"])

    update.message.reply_text(
        "Your expense "+str(oid_selected["name"])+" of "+str(oid_selected["price"])+"€ has been deleted!",
        reply_markup=markup
    )

    #cleare junk data
    user_data = context.user_data
    user_data.clear()

    return CHOOSING



#Delete expense by providing the list to the user of all the expenses , than the user type the one to delete
def update_expense_choice(update: Update, context: CallbackContext) -> int:
    logger.info("ok adesso")
    list_expenses = myDbManager.getExpensesSelectable(update.message.from_user.id)
    logger.info("ls:"+str(list_expenses))
    message=""
    response_list= []
    for ex in list_expenses:
        response_list.append(str(ex["id"]))
        message += str(ex["id"])+ ") "+str(ex["date"])+"| "+str(ex["name"])+" - "+str(ex["price"])+"€\n\n"

    markup_ids = ReplyKeyboardMarkup(response_list, one_time_keyboard=True)

    update.message.reply_text(
        "Your expenses are:\n"+message,
        reply_markup=markup_ids
    )
    context.user_data['list_expenses'] = list_expenses
    return UPDATE_REPLY

#Recive the user input of the expense to delete and procede with the delete from the db
def update_expense_replay(update: Update, context: CallbackContext) -> int:

    selected = update.message.text

    list_expenses = context.user_data["list_expenses"]

    #get the object id from given a numeric id
    oid_selected = [item for item in list_expenses if str(item["id"]) == str(selected)][0]

    markup_filds= ReplyKeyboardMarkup([["name"],["price"],["date"]], one_time_keyboard=True)

    update.message.reply_text(
        "Which fild of the expense "+str(oid_selected["name"])+" of "+str(oid_selected["price"])+"€"+str(oid_selected["date"])+"."
        "\nwould you like to modify?",
        reply_markup=markup_filds
    )
    context.user_data["oid_selected"] = oid_selected["_id"]

    return UPDATE_CHOOSING

#Recive the user input of the expense to delete and procede with the delete from the db
def update_expense_choicefild(update: Update, context: CallbackContext) -> int:

    selected = update.message.text

    context.user_data["fild_to_update"] = selected

    update.message.reply_text(
        "Plese type the new "+str(selected)+":",
    )

    return UPDATE_MOFIFY

def update_expense_modify(update: Update, context: CallbackContext) -> int:

    new_value_fild = update.message.text

    oid_selected = context.user_data["oid_selected"]
    fild_to_update= context.user_data["fild_to_update"]

    #calling the delete method
    myDbManager.updateExpense(update.message.from_user.id,oid_selected,fild_to_update,new_value_fild)

    update.message.reply_text(
        "The fild "+str(fild_to_update)+" has been update with: "+new_value_fild,
        reply_markup=markup
    )

    #cleare junk data
    user_data = context.user_data
    user_data.clear()

    return CHOOSING




def main():

    """Start the bot."""
    updater = Updater(os.getenv("token"), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^New expense$'), new_expense_choice),
                MessageHandler(Filters.regex('^Show expenses$'), show_expenses_choice),
                MessageHandler(Filters.regex('^Update expense$'), update_expense_choice),
                MessageHandler(Filters.regex('^Delete expense$'),delete_expense_choice),
            ],
            DELETE_REPLY:[
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    delete_expense_replay,
                ),
            ],
            UPDATE_REPLY:[
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    update_expense_replay,
                ),
            ],
            UPDATE_CHOOSING: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    update_expense_choicefild,
                ),
            ],
            UPDATE_MOFIFY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    update_expense_modify,
                ),
            ],
            NEW_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    new_expense_reply,
                ),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), done
                ),
            ],

        },
        
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
