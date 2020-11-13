class Expense():
    _id = None
    name= None
    price = None
    date = None

    def __init__(self,id,name,price,date):
        super().__init__()
        self._id = id
        self.name = name
        self.price = price
        self.date = date


    def getSchema(self):
        return {
            "_id": self._id,
            "name": self.name,
            "price": self.price,
            "date": self.date
        }

    def toString(self):
       return " -name: "+str(self.name)+",\n -price: "+str(self.price)+",\n -date: "+str(self.date);