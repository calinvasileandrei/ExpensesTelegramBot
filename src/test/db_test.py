import pymongo
import os
import urllib
from dotenv import load_dotenv
project_folder = os.path.expanduser('../main')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))


db_user = urllib.parse.quote(os.getenv("db_user"))
db_password = urllib.parse.quote(os.getenv("db_password"))
db_url = urllib.parse.quote(os.getenv("db_url"))

myClient = pymongo.MongoClient("mongodb+srv://"+db_user+":"+db_password+db_url)
myDb = myClient["expenses"]
myUsers = myDb["Users"]

res = myUsers.find()
for el in res:
    print(el)
