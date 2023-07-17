from flask import Flask ,request,render_template,redirect,url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime as dt

app = Flask(__name__,template_folder='template',static_url_path="/static")
cl = MongoClient('mongodb://localhost:27017/')

#database and collections
db = cl['Library']
collection = db['Books']
collection2 = db['members']
collection3 = db['transactions']

#redirecting section
@app.route('/')
def index():
    return render_template("main.html") #Home page

@app.route('/books')
def books():
    book = list(collection.find({}, {'_id': 1, 'name': 1, 'author': 1,'quantity':1}))
    quantity = sum(int(bookk['quantity']) for bookk in book)
    return render_template('books.html', books=book,quantity=quantity)#books page

@app.route('/members')
def members():
    member = collection2.find({}, {'_id': 1, 'memberid': 1, 'name': 1})
    quantity2 = collection2.count_documents({})
    return render_template("members.html",member=member,quantity2=quantity2)#members page

@app.route('/transactions')
def transactions():
    transaction = collection3.find({}) 
    quantity3 = collection3.count_documents({})
    return render_template("transactions.html", transactions=transaction,quantity3=quantity3)#transactions page

#redirecting to adding pages
@app.route('/addbook_pg')
def addbook_pg():
    return render_template('addbook.html')#for adding books

@app.route('/addmember_pg')
def addmember_pg():
    return render_template('addmember.html')#for adding members

@app.route('/addtransaction_pg')
def addtransaction_pg():
    return render_template('addtransactions.html',state=0)#for adding transactions


#searching sections
@app.route('/search',methods=['POST'])
def search():
    data = request.form.get('searc')
    if data!="":
        books = list(collection.find({'$or':[{'name':data},{'author':data}]}))
        quantity = sum(int(bookk['quantity']) for bookk in books )
        print(books)
        return render_template('books.html', books=books,quantity=quantity)
    else:
        return redirect(url_for('books'))#For books search


@app.route('/search2',methods=['POST'])
def search2():
    data = request.form.get('searc')
    if data!= "":
        quantity2 = collection2.count_documents({})
        member = collection2.find({'$or':[{'name':data},{'memberid':data}]})
        return render_template('members.html', member=member,quantity2=quantity2)
    else:
        return redirect(url_for('members'))#for members search

@app.route('/search3',methods=['POST'])
def search3():
    data = request.form.get('searc')
    if data!="":
        quantity3 = collection3.count_documents({})
        transaction = collection3.find({'$or':[{'name':data},{'memberid':data}]})
        return render_template('transactions.html', transactions=transaction,quantity3=quantity3)
    else:
        return redirect(url_for('transactions'))#for transactions search
    

#for deleting operation
@app.route('/delete_book/<book_id>', methods=['GET', 'POST'])
def delete_book(book_id):
    collection.delete_one({'_id':ObjectId(book_id)})
    return redirect(url_for('books'))#for deleting books

@app.route('/delete_member/<member_id>', methods=['GET', 'POST'])
def delete_member(member_id):
    collection2.delete_one({'_id':ObjectId(member_id)})
    return redirect(url_for('members'))#for deleting members

@app.route('/delete_transaction/<transaction_id>', methods=['GET', 'POST'])
def delete_transaction(transaction_id):
    collection3.delete_one({'_id': ObjectId(transaction_id)})
    return redirect(url_for('transactions'))#for deleting transactions


#for adding operation
@app.route('/addbook',methods=['POST'])
def addbook():
    book = {
        '_id': ObjectId(),
        'name':request.form.get('searc'),
        'author':request.form.get('searca'),
        'quantity':int(request.form.get('searcaq')),
    }
    collection.insert_one(book)
    return  redirect(url_for('books'))#to add books


@app.route('/addmember',methods=['POST'])
def addmember():
    member = {
        '_id': ObjectId(),
        'memberid':request.form.get('searc'),
        'name':request.form.get('searca'),
    }
    collection2.insert_one(member)
    return  redirect(url_for('members'))#to add members



@app.route('/addtransaction', methods=['POST'])
def addtransaction():
    date_time = dt.datetime.now()
    transaction = {
        '_id': ObjectId(),
        'memberid': request.form.get('memberid'),
        'name': request.form.get('name'),
        'bookname': request.form.get('bookname'),
        'quantity': request.form.get('quantity'),
        'state': request.form.get('state'),
        'payment': request.form.get('payment'),
        'datetime': date_time.strftime("%c"),
    }
    val = collection.find_one({"name":transaction['bookname']})
    if val and val['quantity']!=0 or transaction['state']=="Returned":
        if transaction['state']=="Not Returned":
            value = int(transaction['quantity'])
            collection.update_one({'name':transaction['bookname']},{'$inc':{'quantity':-value}})
            collection3.insert_one(transaction)
        else:
            value = int(transaction['quantity'])
            collection.update_one({'name':transaction['bookname']},{'$inc':{'quantity':value}})
            collection3.insert_one(transaction)
    else:
        return render_template('addtransactions.html',state=1)

    return redirect(url_for('transactions'))#to add transactions


if __name__ == "__main__":
    app.run(debug=True)
