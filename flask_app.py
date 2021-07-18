from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from flask_mail import Mail, Message
import random
import fun
import pymysql

app = Flask(__name__)

#password for submitting a new tournament result (universal for all fencers prior to making accounts

@app.route('/')
def index():
    return render_template('index.html',
            page_title="AFA Virtual Leaderboard",)

@app.route('/submitResult/', methods=['GET', 'POST'])
def submit_result():
    conn = pymysql.connect(
            )
    if request.method == 'POST':
        result_inserted = False
        try:
            '''password = request.form.get('password-ts')
            if password != PSW:
                activeFencers = fun.get_all_active_fencers(conn)
                return render_template('submitResult.html',
                        flashedMessage = "Wrong password; result not submitted.",
                        result_inserted = 'Failure',
                        page_title="Result Submission",
                        activeFencers = activeFencers)'''
            fencer_id = int(request.form.get('nameForm'))
            tournament_name = request.form.get('tournamentName')
            tournament_type = request.form.get('tournamentType')
            tournament_year = request.form.get('tournamentDate')
            tournament_date = tournament_year + "-00-00"
            fencer_place = int(request.form.get('placement'))
            num_competitors = int(request.form.get('numCompetitors'))
            division = request.form.get('division')
            weapon = request.form.get('weaponType')
            ev = request.form.get('eventType')
            event_type = ev
            if division == "Women":
                event_type += "W"
            else:
                event_type += "M"
            if weapon == "Foil":
                event_type += "F"
            else:
                event_type += "E"
            result_inserted = fun.insert_tournament_result(conn, fencer_id, tournament_name,
                tournament_type, tournament_date, event_type, fencer_place,
                num_competitors)
        except Exception as err:
            print(err)
        return render_template('index.html',
            page_title="AFA Virtual Leaderboard",
            result_inserted = result_inserted,
            flashedMessage = "Tournament result was successfully submitted!")
    else: #get
        activeFencers = fun.get_all_active_fencers(conn)
        return render_template('submitResult.html', page_title="Result Submission",
                        activeFencers = activeFencers)

@app.route('/specificEvent/<eventCode>', methods= ['GET', 'POST'])
def specificEvent(eventCode):
    events = {'D1WE': "D1 Women's Epee", 'D1AWE': "D1A Women's Epee", 'D2WE': "D2 Women's Epee",
              'D3WE': "D3 Women's Epee", 'JNRWE': "Junior Women's Epee", 'CDTWE': "Cadet Women's Epee",
              'Y14WE': "Y14 Women's Epee", 'Y12WE': "Y12 Women's Epee", 'Y10WE': "Y10 Women's Epee",
              'V40WE': "VET40 Women's Epee", 'V50WE': "VET50 Women's Epee", 'VETCOWE': "VETCO Women's Epee",
              'D1WF': "D1 Women's Foil", 'D1AWF': "D1A Women's Foil", 'D2WF': "D2 Women's Foil",
              'D3WF': "D3 Women's Foil", 'JNRWF': "Junior Women's Foil", 'CDTWF': "Cadet Women's Foil",
              'Y14WF': "Y14 Women's Foil", 'Y12WF': "Y12 Women's Foil", 'Y10WF': "Y10 Women's Foil",
              'V40WF': "VET40 Women's Foil", 'V50WF': "VET50 Women's Foil", 'VETCOWF': "VETCO Women's Foil",
              'D1ME': "D1 Men's Epee", 'D1AME': "D1A Men's Epee", 'D2ME': "D2 Men's Epee",
              'D3ME': "D3 Men's Epee", 'JNRME': "Junior Men's Epee", 'CDTME': "Cadet Men's Epee",
              'Y14ME': "Y14 Men's Epee", 'Y12ME': "Y12 Men's Epee", 'Y10ME': "Y10 Men's Epee",
              'V40ME': "VET40 Men's Epee", 'V50ME': "VET50 Men's Epee", 'VETCOME': "VETCO Men's Epee",
              'D1MF': "D1 Men's Foil", 'D1AMF': "D1A Men's Foil", 'D2MF': "D2 Men's Foil",
              'D3MF': "D3 Men's Foil", 'JNRMF': "Junior Men's Foil", 'CDTMF': "Cadet Men's Foil",
              'Y14MF': "Y14 Men's Foil", 'Y12MF': "Y12 Men's Foil", 'Y10MF': "Y10 Men's Foil",
              'V40MF': "V40 Men's Foil", 'V50MF': "VET50 Men's Foil", 'VETCOMF': "VETCO Men's Foil",
              }
    eventName = events[eventCode]
    conn = pymysql.connect(
            )
    topThree = True
    allTypes = fun.get_top_three_fencers(conn, eventCode)
    forNational = allTypes["National"]
    forRegional = allTypes["Regional"]
    if request.method == "POST":
        topOrAll = request.form.get('topOrAll')
        # print("topOrAll:", topOrAll)
        if topOrAll == "View All Results":
            topThree = False
            allTypes = fun.get_all_fencers(conn, eventCode)
            forNational = allTypes["National"]
            forRegional = allTypes["Regional"]
        elif topOrAll == "View Personal Bests":
            topThree = True
            allTypes = fun.get_top_three_fencers(conn, eventCode)
            forNational = allTypes["National"]
            forRegional = allTypes["Regional"]
    topOrAll_title = "(Personal Bests)" if topThree else "(All Results)"
    return render_template('event.html',
            page_title="AFA Virtual Leaderboard",
            eventName = eventName, forNational=forNational,
            forRegional = forRegional,
            topThree = topThree,
            topOrAll_title = topOrAll_title)

@app.route('/addFencer/', methods=['GET', 'POST'])
def addFencer():
    if request.method == "GET":
        return render_template("addFencer.html", page_title="Adding new fencer")
    else:
        password = request.form.get('password-ts')
        if password != PSW:
            return render_template('addFencer.html',
                    flashedMessage = "Wrong password; fencer not added to database.",
                    result_inserted = 'Failure',
                    page_title="Adding new fencer")
        result_inserted = False
        try:
            conn = pymysql.connect(
            )
            firstName = request.form.get("firstName")
            middleName = request.form.get("middleName")
            lastName = request.form.get("lastName")
            fencingID = int(request.form.get("fencingID"))
            isAC = request.form.get("isActiveCompeting")
            active = 1
            if isAC == "No":
                active = 0
            result_inserted = fun.insert_fencer(conn, fencingID, firstName, middleName,
                lastName, active)
            activeFencers = fun.get_all_active_fencers(conn)
            if result_inserted != True:
                flashedMessage = result_inserted
                return render_template('submitResult.html',
                    page_title="AFA Virtual Leaderboard",
                    flashedMessage = flashedMessage,
                    result_inserted = result_inserted,
                    activeFencers = activeFencers)
        except Exception as err:
            print("Cannot insert new fencer. Error:", err)
        return render_template('submitResult.html',
            page_title="AFA Virtual Leaderboard",
            result_inserted = result_inserted,
            flashedMessage = "New fencer has been inserted into database!",
            activeFencers = activeFencers)

###########################################################################################################
# NEW CODE!!!!!!!!!!!!!!!!
###########################################################################################################

@app.route('/records')
#this function displays the tournament records for a user
def view_records():
    conn = pymysql.connect(
            )
    if "id" in session: #if the user's logged in
        usrnm = session["id"]
        if usrnm == 0:
            cur = conn.cursor(pymysql.cursors.DictCursor)
            #cur.execute("""SELECT id,tournament_name,tournament_type,
            #    tournament_date, event_type, fencer_place, num_competitors,fencer_id FROM record""")
            #userDetails = cur.fetchall()
            #cur.execute('''SELECT first_name, last_name, middle_name,fencer_id from fencer''')
            #userNames = cur.fetchall()
            cur.execute('''SELECT fencer.first_name, fencer.last_name,fencer.middle_name,
            record.id,record.tournament_name,record.tournament_type,
            record.tournament_date, record.event_type, record.fencer_place, record.num_competitors,record.fencer_id
            FROM fencer INNER JOIN record on fencer.fencer_id = record.fencer_id''')
            userDetails = cur.fetchall()
            return render_template('recordsadmin.html', userDetails = userDetails)
        try:
            cur = conn.cursor(pymysql.cursors.DictCursor)
        #select all usrnm related tournaments
            resultValue = cur.execute('''SELECT id,tournament_name,tournament_type,
                tournament_date, event_type, fencer_place, num_competitors,fencer_id
                FROM record WHERE fencer_id = %(usrnm)s''',{'usrnm':usrnm})
            if resultValue > 0:
                #userDetails contains all usrnm related tournaments
                userDetails = cur.fetchall()
                cur.execute('''SELECT first_name, last_name, middle_name,fencer_id from fencer WHERE fencer_id=%(usrnm)s''',{'usrnm':usrnm})
                userNames = cur.fetchall()
                #this return statement passes userDetails into another value also called userDetails in records.html, where
                #the latter will be used for displaying the data
                return render_template('records.html',userDetails = userDetails,userNames = userNames)
            else:
                return render_template("noRecords.html")

        except Exception as err:
            print("Cannot get tournament records for {}, because of {}".format(usrnm, err))
            return redirect(url_for("login"))
    else: #if the user's not logged in
        return redirect(url_for("login"))

@app.route('/records',methods=["POST","GET"])
#this function changes the data in the database once the edit form is submitted
def choose_records():
            conn = pymysql.connect(
            )
            if request.method == 'POST':
                try:
                    curs = conn.cursor(pymysql.cursors.DictCursor)
                    tournamentID = str(request.form.get("tournamentID"))
                    curs.execute('''SELECT * FROM record WHERE id=%(tournamentID)s''',{'tournamentID':tournamentID})
                    global details
                    details = curs.fetchall()
                    #return "hellow world 1"
                    #return render_template("edit.html")#,tournament_name = details['tournament_name']
                    #,tournament_date=str(details['tournament_date'])[:3],fencer_place=details['fencer_place'],
                    #num_competitors=details['num_competitors'])
                    return redirect(url_for("editPage"))#,details=details
                except Exception as err:
                    print("Cannot edit record because:", err)
                    return redirect(url_for("view_records"))
            else:
                return redirect(url_for("index"))
@app.route('/edit/')
def editPage():
    #tournament_names=details["tournament_name"]
    return render_template('edit.html',details=details)#[0]["tournament_name"]

@app.route('/edit/',methods=["GET","POST"])
#this function changes the data in the database once the edit form is submitted
def editForm():
    conn = pymysql.connect(
            )
    if request.method == "POST":
        try:
            curs = conn.cursor(pymysql.cursors.DictCursor)
            tournament_id = int(request.form.get("tournamentID"))
            tournamentName = request.form.get('tournamentName')
            tournamentType = request.form.get('tournamentType')
            tournamentYear = request.form.get('tournamentDate')+ "-00-00"
            fencerPlace = int(request.form.get('placement'))
            numCompetitors = int(request.form.get('numCompetitors'))
            division = request.form.get('division')
            weapon = request.form.get('weaponType')
            ev = request.form.get('eventType')
            eventType = ev
            if division == "Women":
                eventType += "W"
            else:
                eventType += "M"
            if weapon == "Foil":
                eventType += "F"
            else:
                eventType += "E"
            exe = '''UPDATE record SET tournament_name =%(tournamentName)s,
                tournament_type =%(tournamentType)s , tournament_date =%(tournamentYear)s,
                event_type =%(eventType)s, fencer_place =%(fencerPlace)s, num_competitors =
                 %(numCompetitors)s WHERE id = %(tournament_id)s'''
            curs.execute(exe,{'tournamentName':tournamentName,'tournamentType':tournamentType,
                'tournamentYear':tournamentYear,'eventType':eventType,'fencerPlace':fencerPlace,
                'numCompetitors':numCompetitors,'tournament_id':tournament_id})
            conn.commit()
            flash("Your change has been saved!")
            return redirect(url_for("view_records"))
        except Exception as err:
            print("Cannot edit record because:", err)
            return redirect(url_for("view_records"))
    else:
        return redirect(url_for("index"))

@app.route('/login/')
def login():
 return render_template("logIn.html")

@app.route('/login/',methods=['POST','GET'])
def portal():
    try:
        if request.method == 'POST':
            username = str(request.form.get('nm'))
            password = str(request.form.get('password'))
            conn = pymysql.connect(
                )
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = """SELECT * FROM accounts WHERE username = %s AND password = %s"""
            cursor.execute(query, (username, password))
            current = cursor.fetchone()
            if current:
                session['loggedin'] = True
                session['id'] = current['fencer_id']
                session['user'] = current['username']
                flash("Logged In!")
                return redirect(url_for('index'))
            else:
                flash("Incorrect Username or Password")
                return render_template("logIn.html")
    except Exception as err:
        print("Login failed...", err)


@app.route('/logout/')
def logout():
    session.pop('user',None)
    session.pop('id', None)
    session.pop('loggedin', None)
    flash("You have been logged out")
    return redirect(url_for('login')) #render_template("LoggedIn.html", flashedmessage = "You have been logged out!")


@app.route('/signUp/')#,methods=['POST','GET']
def signUp():
    return render_template('signUp.html')

@app.route('/signUp/', methods =['POST', 'GET'])
def register():
    conn = pymysql.connect(
                    )

    if request.method == 'POST':
        try:
            fname = str(request.form.get('firstName'))
            mname = str(request.form.get('middleName'))
            lname = str(request.form.get('lastName'))
            fencerid = int(request.form.get('fencingID'))
            gender = str(request.form.get('gender'))
            password = str(request.form.get('password'))
            email = request.form.get('email')
            username = request.form.get('nm')
            active = request.form.get('isActiveCompeting')  #Yes or No string

            cursor = conn.cursor(pymysql.cursors.DictCursor)

            #account exists everywhere
            query = """SELECT * FROM accounts WHERE fencer_id = %s """
            cursor.execute(query, (fencerid))
            current = cursor.fetchone()
            if current:
                email = current['email']
                flash("Account already exists! Attached email: " + email)
                return redirect(url_for('login'))

            #username taken
            query = '''SELECT * FROM accounts WHERE username = %s '''
            cursor.execute(query, (username))
            current = cursor.fetchall()
            if current:
                flash("Username taken!")
                return render_template('signUp.html')
            #email taken
            query = """SELECT * FROM accounts WHERE email = %s """
            cursor.execute(query, (email))
            current = cursor.fetchone()

            if current:
                flash("Email taken!")
                return render_template('signUp.html')

            #after signing up, will log you in
            else:
                if active == "Yes":
                    active1 = 1
                elif active == "No":
                    active1 = 0

                #new account, update active
                query = '''SELECT * FROM fencer WHERE fencer_id = %s'''
                cursor.execute(query, (fencerid))
                current = cursor.fetchall()
                if current:
                    query = """UPDATE fencer SET active = %s WHERE fencer_id = %s"""
                    cursor.execute(query, (active1, fencerid))
                    fun.addAccount(conn, fencerid, gender, username, password, email)
                    flash("You have successfully reigistered!")
                    session['loggedin'] = True
                    session['id'] = fencerid
                    session['user'] = username
                    return redirect(url_for('index'))
                #new fencer, new account
                else:
                    fun.insert_fencer(conn, fencerid, fname, mname, lname, active1)
                    fun.addAccount(conn, fencerid, gender, username, password, email)
                    flash("You have successfully reigistered!")
                    session['loggedin'] = True
                    session['id'] = fencerid
                    session['user'] = username
                    return redirect(url_for('index'))

        except Exception as err:
            print("Sign up failed: ", err)
            return render_template('signUp.html')
    else:
        return render_template('signUp.html')


mail = Mail(app)

@app.route('/forgotcredentials/')
def password():
    return render_template('forgotcredentials.html')

@app.route('/forgotcredentials/', methods = ['POST', 'GET'])
def send_password():
    try:
        if request.method == 'POST':
            email = request.form.get('email')

            conn = pymysql.connect(
                        )
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            query = """SELECT * FROM accounts WHERE email = %s"""
            cursor.execute(query, (email))
            current = cursor.fetchone()

            if not current:
                flash("Email is not attached to any account. Please try a different email.")
                return render_template('forgotcredentials.html')

            else:
                PASSWORD = current['password']
                USERNAME = current['username']
                msg = Message("Forgotten Credentials", sender = "", recipients = [email])
                msg.body = ("Dear user,\r\n\r\nIf you are not a Apex Fencing Academy user, please disregard this email.\r\n\r\nYour credentials are:\r\nUsername: " +
                USERNAME + "\r\nPassword: " + PASSWORD + "\r\n\r\nLog in at https://testapex.pythonanywhere.com/login/")
                mail.send(msg)
                flash("Email sent with your information")
                return redirect(url_for('login'))

    except Exception as err:
        print(err)
        return "The email could not be sent. Please contact admin for help."


#MYPROFILE
@app.route('/myProfile/')
def access_profile():
    conn = pymysql.connect(
                        )
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if "id" in session: #if the user's logged in
        usrID = session["id"]
        cur.execute('''select * from fencer where fencer_id=%(usrID)s''',{'usrID':usrID})
        global fencer
        fencer = cur.fetchall()
        cur.execute("select * from accounts where fencer_id=%(usrID)s",{'usrID':usrID})
        global accounts
        accounts = cur.fetchall()
        return render_template('myProfile.html',fencer = fencer, accounts=accounts)
    else: #if the user's not logged in
        return redirect(url_for("login"))

@app.route('/editProfile/')
def showProfile():
    return render_template('editProfile.html', fencer=fencer, accounts=accounts)

@app.route('/editProfile/',methods=['POST','GET'])
def edit_profile():
    conn = pymysql.connect(
            )

    try:
        if request.method == 'POST':
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            #might need to change names for form
            fname = request.form.get('firstName')
            mname = request.form.get('middleName')
            lname = request.form.get('lastName')
            fencerID = request.form.get('fencingID') #int
            newemail = str(request.form.get('email'))
            gender = request.form.get('gender')
            active = request.form.get('active') #need to make into a number (1 or 0)
            username = request.form.get('username')
            password = request.form.get('password')

            #have to check for email, username, and fencingid for copies in database

            if str(fencer[0]['fencer_id']) != str(fencerID):
                query = """SELECT * FROM accounts WHERE fencer_id = %s """
                cursor.execute(query, (fencerID))
                current = cursor.fetchone()
                if current:
                    flash("Fencing ID taken")
                    return render_template('editProfile.html', fencer=fencer, accounts=accounts)

                query = """UPDATE fencer SET fencer_id = %s WHERE fencer_id = %s"""
                cursor.execute(query, (fencerID, fencer[0]['fencer_id']))

            #FENCER
            query = '''UPDATE fencer SET {} = %s WHERE fencer_id = %s'''

            if fencer[0]['first_name'] != fname:
                cursor.execute(query.format('first_name'), (fname, fencerID))

            if fencer[0]['middle_name'] != mname:
                cursor.execute(query.format('middle_name'), (mname, fencerID))

            if fencer[0]['last_name'] != lname:
                cursor.execute(query.format('last_name'), (lname, fencerID))

            #should be a number
            if active == "Yes":
                active1 = 1
            elif active == "No":
                active1 = 0
            if fencer[0]['active'] != active1:
                cursor.execute(query.format('active'), (active1, fencerID))

            #ACCOUNTS
            query = '''UPDATE accounts SET {} = %s WHERE fencer_id = %s'''

            if accounts[0]['email'] != newemail:
                query = """SELECT * FROM accounts WHERE email = %s """
                cursor.execute(query, (newemail))
                current = cursor.fetchone()
                if current:
                    flash("Email taken")
                    return render_template('editProfile.html', fencer=fencer, accounts=accounts)
                cursor.execute('''UPDATE accounts SET email = %s WHERE fencer_id = %s''', (newemail, fencerID))

            if accounts[0]['gender'] != gender:
                cursor.execute('''UPDATE accounts SET gender = %s WHERE fencer_id = %s''', (gender, fencerID))

            if accounts[0]['username'] != username:
                query = """SELECT * FROM accounts WHERE username = %s """
                cursor.execute(query, (username))
                current = cursor.fetchone()
                if current:
                    flash("Username taken")
                    return render_template('editProfile.html', fencer=fencer, accounts=accounts)
                cursor.execute('''UPDATE accounts SET username = %s WHERE fencer_id = %s''', (username, fencerID))

            if accounts[0]['password'] != password:
                cursor.execute('''UPDATE accounts SET password = %s WHERE fencer_id = %s''', (password, fencerID))

            #fun.changeInfo(conn, fname, mname, lname, fencerID, email, gender, active, username, password)
            session['id'] = fencerID
            session['user'] = username
            conn.commit()
            flash("Account information updated!")
            return redirect(url_for('access_profile'))
        else:
            return "Else"
    except Exception as err:
        return "exception: " + str(err)
        print("Edit failed...", err)



if __name__ == '__main__':
    app.debug = True
    app.run()
