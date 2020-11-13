import pymongo
import os
import urllib
from src.main.database.user.user import User
from src.main.database.expense.expense import Expense
from dotenv import load_dotenv
from src.main.utils.base_logger import logger
from bson import ObjectId

project_folder = os.path.expanduser('./')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

#getting the db data
db_user = urllib.parse.quote(os.getenv("db_user"))
db_password = urllib.parse.quote(os.getenv("db_password"))
db_url = urllib.parse.quote(os.getenv("db_url"))

#creating the mongo client
myClient = pymongo.MongoClient("mongodb+srv://"+db_user+":"+db_password+"@"+db_url)
#getting the db and users collections
myDb = myClient["expenses"]
myUsers = myDb["Users"]



#USER
def newUser(info):
    user= User(info.id,info.first_name,info.username)

    if(exists(user)):
        logger.info("User exists")
    else:
        createUserDB(user)

def createUserDB(user):
    response= myUsers.insert_one(user.getSchema())
    logger.info("New user create with id:"+str(response.inserted_id))

def exists(user):
    response = myUsers.find_one({"id":user.id},{"id":1})
    logger.info("find_one user: "+str(response))
    if(response != None):
        return True
    else:
        return False


#EXPENSES

def createExpense(userid,text):
    data = text.split(",")
    new_id = ObjectId()
    new_expense = Expense(new_id,data[0],data[1],data[2])
    response = myUsers.update({"id":userid}, {'$push': {'expenses': new_expense.getSchema()}})
    logger.info("elements updated: "+str(response["updatedExisting"]))
    return new_expense.toString()

def deleteExpense(userid,expense_id):
    response = myUsers.update({"id":userid}, {'$pull': {'expenses': {"_id":ObjectId(str(expense_id))}}})

def updateExpense(userid,expense_id,fild_to_update,new_value_fild):
    response = myUsers.update({"id":userid,'expenses._id': ObjectId(str(expense_id))},
                              {'$set': {"expenses.$."+str(fild_to_update):str(new_value_fild)}})

def getExpenses(userid):
    expenses = myUsers.find_one({"id":userid},{"expenses":1})
    list_expenses = ""
    for ex in expenses["expenses"]:
        list_expenses+= "* "+str(ex["date"])+"| "+str(ex["name"])+" - "+str(ex["price"])+"€\n\n"

    return list_expenses


def getExpensesSelectable(userid):
    expenses = myUsers.find_one({"id":userid},{"expenses":1})
    list_expenses = []
    i=1
    for ex in expenses["expenses"]:
        list_expenses.append({
            "_id":ObjectId(ex["_id"]),
            "id":i,
            "name":ex["name"],
            "price":ex["price"],
            "date":ex["date"]
            })
        i+=1

    return list_expenses