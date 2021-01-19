from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)


app.secret_key = "flash message"

#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'sadafa57'
#app.config['MYSQL_DB'] = 'appinfosys1'

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'N1zrBvTF50'
app.config['MYSQL_PASSWORD'] = 'VunC1MgBOS'
app.config['MYSQL_DB'] = 'N1zrBvTF50'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/forward/", methods=['POST'])
def move_forward():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user_table WHERE TC = %s AND Password = %s', (username, password))
        # Fetch one record and return result
        account = cur.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['TC'] = account[0]
            session['FLATNUMBER'] = account[7]
            session['IsAdmin'] = account[5]
            # Redirect to home page
            if session['IsAdmin'] == 0:
                return render_template('user/userdashboard.html')
            else:
                return render_template('admin/admindashboard.html')
        else:
            # Account doesnt exist or username/password incorrect
            error = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', error=error)


@app.route('/admindashboard')
def admindashboard():
    if session.get('loggedin') == True:
        return render_template('admin/admindashboard.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('TC', None)
    session.pop('FLATNUMBER', None)
    session.pop('IsAdmin', None)
    return render_template('login.html')


#-----------------------User Operations

@app.route('/useroperations')
def useroperations():
    if session.get('loggedin') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_table ORDER BY Flat")
        data = cur.fetchall()
        cur.close()
        return render_template('admin/useroperations.html', users=data)
    return render_template('login.html')


@app.route('/searchbyFlatNumber', methods=['GET', 'POST'])
def searchbyFlatNumber():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        searchFlat = request.form['searchName']
        cur.execute('SELECT * FROM user_table WHERE Flat = {0} GROUP BY TC'.format(searchFlat))
        data = cur.fetchall()
        cur.close()
        return render_template('admin/useroperations.html', users=data)


@app.route('/insertperson', methods=['POST'])
def insertperson():
    if  request.method == "POST":
        tc = request.form['tc']
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        blood = request.form['blood']
        role = request.form['role']
        password = request.form['password']
        flat = request.form['flat']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_table WHERE TC = {}".format(tc))
        # Fetch one record and return result
        account = cur.fetchone()
        # If account exists in accounts table in out database
        if account:
            flash("Person is already inserted")
        else:
            flash("Person inserted successfully")
            cur.execute("INSERT INTO user_table (TC,FirstName,LastName, Phone, BloodType, IsAdmin, Password, Flat) VALUES (%s, %s, %s, %s,%s,%s,%s,%s)",(tc, name, surname, phone, blood, role, password, flat))
            mysql.connection.commit()
        return redirect(url_for('useroperations'))


@app.route('/updateperson', methods=['POST'])
def updateperson():
    if  request.method == "POST":
        flash("Person updated successfully")
        tc = request.form['tc']
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        blood = request.form['blood']
        password = request.form['password']
        flat = request.form['flat']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE user_table SET FirstName=%s, LastName=%s , Phone=%s , BloodType=%s, Password=%s, Flat=%s WHERE TC = %s""", (name, surname, phone, blood, password, flat, tc))
        mysql.connection.commit()
        return redirect(url_for('useroperations'))


@app.route('/deleteperson/<string:tc_data>', methods=['POST', 'GET'])
def deleteperson(tc_data):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM user_table WHERE TC = {0}".format(tc_data))
        mysql.connection.commit()
        flash("Person : {0} deletedted successfully".format(tc_data))
        return redirect(url_for('useroperations'))


#----------------------User Operations END

#----------------------DEBT Operations

@app.route('/debtoperations')
def debtoperations():
    if session.get('loggedin') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM debt_table")
        data = cur.fetchall()
        cur.close()
        return render_template('admin/debtoperations.html', debts=data)
    return render_template('login.html')


@app.route('/searchbyFlatNumberDebt', methods=['GET', 'POST'])
def searchbyFlatNumberDebt():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        searchFlat = request.form['searchName']
        cur.execute('SELECT * FROM debt_table WHERE FlatNumber = {0} GROUP BY DebtId'.format(searchFlat))
        data = cur.fetchall()
        cur.close()
        return render_template('admin/debtoperations.html', debts=data)


@app.route('/insertdebt', methods=['POST'])
def insertdebt():
    if  request.method == "POST":
        flash("Debt inserted successfully")
        name = request.form['name']
        total = request.form['total']
        flatnumber = request.form['flat']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO debt_table (DebtName,Total,FlatNumber) VALUES (%s, %s, %s)", (name, total, flatnumber))
        mysql.connection.commit()
        return redirect(url_for('debtoperations'))


@app.route('/updatedebt', methods=['POST'])
def updatedebt():
    if  request.method == "POST":
        flash("Debt updated successfully")
        id = request.form['id']
        name = request.form['name']
        total = request.form['total']
        flatnumber = request.form['flat']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE debt_table SET DebtName=%s, Total=%s , FlatNumber=%s WHERE DebtId = %s""", (name, total, flatnumber, id))
        mysql.connection.commit()
        return redirect(url_for('debtoperations'))


@app.route('/deletedebt/<string:id_data>', methods=['POST', 'GET'])
def deletedebt(id_data):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM debt_table WHERE DebtId = {0}".format(id_data))
        mysql.connection.commit()
        flash("Debt : {0} deletedted successfully".format(id_data))
        return redirect(url_for('debtoperations'))

#-------------------------END DEBT OPERATIONS

#----------------------FLAT Operations



@app.route('/flatoperations')
def flatoperations():

    if session.get('loggedin') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM flat_table")
        data = cur.fetchall()
        cur.close()
        return render_template('admin/flatoperations.html', flats=data)
    return render_template('login.html')


@app.route('/searchbyFloorNumberFlat', methods=['GET', 'POST'])
def searchbyFloorNumberFlat():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        searchFloor = request.form['searchName']
        cur.execute('SELECT * FROM flat_table WHERE Floor = {0} ORDER BY Floor'.format(searchFloor))
        data = cur.fetchall()
        cur.close()
        return render_template('admin/flatoperations.html', flats=data)


@app.route('/insertflat', methods=['POST'])
def insertflat():
    if  request.method == "POST":
        flash("Flat inserted successfully")
        FlatNumber = request.form['flatnumber']
        floor = request.form['floor']
        IsBaloncy = request.form['baloncy']
        noRooms = request.form['room']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO flat_table (FlatNumber,Floor,IsBaloncy,NoRooms) VALUES (%s, %s, %s, %s)", (FlatNumber, floor, IsBaloncy, noRooms))
        mysql.connection.commit()
        return redirect(url_for('flatoperations'))


@app.route('/updateflat', methods=['POST'])
def updateflat():
    if  request.method == "POST":
        flash("Flat updated successfully")
        FlatNumber = request.form['flatnumber']
        floor = request.form['floor']
        IsBaloncy = request.form['baloncy']
        noRooms = request.form['room']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE flat_table SET Floor=%s , IsBaloncy=%s, NoRooms=%s WHERE FlatNumber = %s""", (floor, IsBaloncy, noRooms, FlatNumber))
        mysql.connection.commit()
        return redirect(url_for('flatoperations'))


@app.route('/deleteflat/<string:flatNumber_data>', methods=['POST', 'GET'])
def deleteflat(flatNumber_data):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM flat_table WHERE FlatNumber = {0}".format(flatNumber_data))
        mysql.connection.commit()
        flash("Flat : {0} deletedted successfully".format(flatNumber_data))
        return redirect(url_for('flatoperations'))

#-------------------------END FLAT OPERATIONS

#----------------------EXPENSE Operations

@app.route('/expenseoperations')
def expenseoperations():
    if session.get('loggedin') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM expense_table")
        data = cur.fetchall()
        cur.close()
        return render_template('admin/expenseoperations.html', expenses=data)
    return render_template('login.html')

@app.route('/searchbyDateExpense', methods=['GET', 'POST'])
def searchbyDateExpense():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        date1 = request.form['date1']
        date2 = request.form['date2']
        cur.execute('SELECT * FROM expense_table WHERE  DATE(ExDate) BETWEEN %s AND %s ORDER BY Date', (date1, date2))
        data = cur.fetchall()
        cur.close()
        return render_template('admin/expenseoperations.html', expenses=data)


@app.route('/insertexpense', methods=['POST'])
def insertexpense():
    if  request.method == "POST":
        flash("Expense inserted successfully")
        exname = request.form['name']
        total = request.form['total']
        date = request.form['date']
        tc = session['TC']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO expense_table (ExName,Total,ExDate,TC) VALUES (%s, %s, %s, %s)", (exname, total, date, tc))
        mysql.connection.commit()
        return redirect(url_for('expenseoperations'))


@app.route('/updateexpense', methods=['POST'])
def updateexpense():
    if  request.method == "POST":
        flash("Expense updated successfully")
        id = request.form['id']
        exname = request.form['name']
        date = request.form['date']
        total = request.form['total']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE expense_table SET ExName=%s , Total=%s, ExDate=%s WHERE ExId = %s""", (exname, total, date, id))
        mysql.connection.commit()
        return redirect(url_for('expenseoperations'))


@app.route('/deleteexpense/<int:id_data>', methods=['POST', 'GET'])
def deleteexpense(id_data):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM expense_table WHERE ExId = {0}".format(id_data))
        mysql.connection.commit()
        flash("Expense : {0} deletedted successfully".format(id_data))
        return redirect(url_for('expenseoperations'))

#-------------------------END EXPENSE OPERATIONS


#----------------------Announcement Operations

@app.route('/announcementoperations')
def announcementoperations():
    if session.get('loggedin') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM announcement_table ORDER BY AnDate")
        data = cur.fetchall()
        cur.close()
        return render_template('admin/announcementoperations.html', announcements=data)
    return render_template('login.html')

@app.route('/searchbyDateAnnouncement', methods=['GET', 'POST'])
def searchbyDateAnnouncement():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        date1 = request.form['date1']
        date2 = request.form['date2']
        cur.execute('SELECT * FROM announcement_table WHERE  DATE(AnDate) BETWEEN %s AND %s ORDER BY AnDate', (date1, date2))
        data = cur.fetchall()
        cur.close()
        return render_template('admin/announcementoperations.html', announcements=data)


@app.route('/insertannouncement', methods=['POST'])
def insertannouncement():
    if  request.method == "POST":
        flash("Announcement inserted successfully")
        date = request.form['date']
        title = request.form['title']
        text = request.form['text']
        tc = session['TC']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO announcement_table (Title,AnText,AnDate,TC) VALUES (%s, %s, %s, %s)", (title, text,date, tc))
        mysql.connection.commit()
        return redirect(url_for('announcementoperations'))


@app.route('/updateannouncement', methods=['POST'])
def updateannouncement():
    if  request.method == "POST":
        flash("Announcement updated successfully")
        id = request.form['id']
        title = request.form['title']
        text = request.form['text']
        date = request.form['date']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE announcement_table SET Title=%s, AnText=%s, AnDate=%s WHERE AnId = %s""", (title, text, date, id))
        mysql.connection.commit()
        return redirect(url_for('announcementoperations'))


@app.route('/deleteannouncement/<int:id_data>', methods=['POST', 'GET'])
def deleteannouncement(id_data):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM announcement_table WHERE AnId = {0}".format(id_data))
        mysql.connection.commit()
        flash("Announcement : {0} deletedted successfully".format(id_data))
        return redirect(url_for('announcementoperations'))

#-------------------------END ANNOUNCEMENT OPERATIONS

#------adminreportoperations

@app.route('/adminreportoperations')
def adminreportoperations():
    if session.get('loggedin') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT flat_table.Floor, flat_table.FlatNumber, debt_table.Total FROM debt_table INNER JOIN flat_table ON debt_table.FlatNumber = flat_table.FlatNumber ORDER BY flat_table.Floor")
        data = cur.fetchall()
        cur.execute("SELECT flat_table.Floor, user_table.FirstName, user_table.LastName, user_table.BloodType FROM user_table LEFT JOIN flat_table ON user_table.Flat = flat_table.FlatNumber ORDER BY flat_table.Floor")
        data2 = cur.fetchall()
        cur.close()
        return render_template('admin/adminreportoperations.html', veriler=data, veriler2=data2)
    return render_template('login.html')

#------------------------- USER (PERSON)


@app.route('/userdashboard')
def userdashboard():
    if session.get('loggedin') == True:
        return render_template('user/userdashboard.html')
    return render_template('login.html')
#-------------MY DEBTS

@app.route('/mydebts')
def mydebts():
    if session.get('loggedin') == True:
        cur = mysql.connection.cursor()
        flatNumber = session['FLATNUMBER']
        # flatNumber=1
        cur.execute("SELECT * FROM debt_table WHERE FlatNumber={}".format(flatNumber))
        data = cur.fetchall()
        cur.execute("SELECT COUNT(DebtId) FROM debt_table WHERE FlatNumber={} GROUP BY FlatNumber".format(flatNumber))
        dataCount = cur.fetchall()
        cur.execute("SELECT SUM(Total) FROM debt_table WHERE FlatNumber={} GROUP BY FlatNumber".format(flatNumber))
        dataSum = cur.fetchall()
        cur.execute("SELECT MAX(Total) FROM debt_table WHERE FlatNumber={} GROUP BY FlatNumber".format(flatNumber))
        dataMax = cur.fetchall()
        cur.execute("SELECT MIN(Total) FROM debt_table WHERE FlatNumber={} GROUP BY FlatNumber".format(flatNumber))
        dataMin = cur.fetchall()
        cur.execute("SELECT AVG(Total) FROM debt_table WHERE FlatNumber={} GROUP BY FlatNumber".format(flatNumber))
        dataAVG = cur.fetchall()
        my_list = [dataCount, dataMin, dataMax, dataSum, dataAVG]
        cur.close()
        return render_template('user/mydebts.html', debts=data, dataList=my_list)
    return render_template('login.html')



@app.route('/paymydebt/<int:id_data>', methods=['POST', 'GET'])
def paymydebt(id_data):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM debt_table WHERE DebtId = {0}".format(id_data))
        mysql.connection.commit()
        flash("Debt : {0} pay successfully".format(id_data))
        return redirect(url_for('mydebts'))

#-------------USER ANNOUNCEMENTS

@app.route('/allannouncements')
def allannouncements():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM announcement_table ORDER BY AnDate")
    data = cur.fetchall()
    cur.close()
    return render_template('user/allannouncements.html', announcements=data)

#------------END USER ANNOUNCEMENTS

@app.route('/reportexpenses')
def reportexpenses():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM expense_table ORDER BY ExDate")
    data = cur.fetchall()
    cur.close()
    return render_template('user/reportexpenses.html', expenses=data)


@app.route('/searchbyDateUserExpense', methods=['GET', 'POST'])
def searchbyDateUserExpense():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        date1 = request.form['date1']
        date2 = request.form['date2']
        cur.execute("SELECT * FROM expense_table Order BY ExDate")
        data = cur.fetchall()
        cur.execute("SELECT COUNT(ExId) FROM expense_table WHERE  DATE(ExDate) BETWEEN %s AND %s GROUP BY ExDate ", (date1, date2))
        dataCount = cur.fetchall()
        cur.execute("SELECT SUM(Total) FROM expense_table WHERE  DATE(ExDate) BETWEEN %s AND %s GROUP BY ExDate", (date1, date2))
        dataSum = cur.fetchall()
        cur.execute("SELECT MAX(Total) FROM expense_table WHERE  DATE(ExDate) BETWEEN %s AND %s GROUP BY ExDate", (date1, date2))
        dataMax = cur.fetchall()
        cur.execute("SELECT MIN(Total) FROM expense_table WHERE  DATE(ExDate) BETWEEN %s AND %s GROUP BY ExDate", (date1, date2))
        dataMin = cur.fetchall()
        cur.execute("SELECT AVG(Total) FROM expense_table WHERE  DATE(ExDate) BETWEEN %s AND %s GROUP BY ExDate", (date1, date2))
        dataAVG = cur.fetchall()
        my_list = [dataCount, dataMin, dataMax, dataSum, dataAVG]
        cur.close()
        return render_template('user/reportexpenses.html', expenses=data, reportlist=my_list)



if __name__ == "__main__":
    app.run(debug=True)