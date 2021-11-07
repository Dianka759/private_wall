from flask_app import app
from flask import render_template,flash,redirect,request,session
from flask_app.models.user import User
from flask_app.models.message import Message

from flask_app.config.mysqlconnection import connectToMySQL

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register",methods=["POST"])
def register():
    if User.validate(request.form):
        pw_hash = bcrypt.generate_password_hash(request.form["password"])
        data = {
        "first_name":request.form["first_name"],
        "last_name":request.form["last_name"],
        "email":request.form["email"],
        "password":pw_hash,
        "confirm_password":pw_hash
        }
        user_id = User.insert_user(data)
        flash("User created! Please login.", "register")  
        # session["user_id"] = user_id       #creates the session
        return redirect("/")
    else:
        return redirect("/")


@app.route("/login",methods=["POST"])
def login():
    user_in_db = User.get_by_email(request.form)
    if not user_in_db:
        flash("invalid email/password", "login")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form["password"]): 
        flash("invalid email/password", "login")
        return redirect("/")
    session["user_id"] = user_in_db.id   # CREATES THE SESSION
    return redirect("/yourpage")


@app.route("/yourpage")
def secret_page():
    if "user_id" not in session:    #checks if you're logged in (the session above exists)
        flash("Must be registered", "register")
        flash("and logged in!", "login")
        return redirect("/")
    else:
        data = {
            "id": session["user_id"]
        }
        user = User.get_user(data)
        recipient_info= User.get_recipient(data)                                                             #displays received messages from users
        sender_info= connectToMySQL("users_schema").query_db("SELECT * FROM users WHERE id != %(id)s", data) #shows all users you can send a message to, not including the logged in user
        total_messages = Message.total_messages(data)                                                        #displays the total messages received from other users 
        sent_messages = Message.count_msg(data)                                                              #counts how many messages the logged in user sent
        
        return render_template("yourpage.html", received=recipient_info, user=user, send=sender_info, sent_messages=sent_messages, total_messages=total_messages)


@app.route("/send", methods=['POST'])           #if message is more than 0 chars, it sends the message to that specific user from the logged in user.
def messages():
    if not Message.validate_msg(request.form):
        return redirect("/yourpage")
    else:
        data = {
            'message': request.form['message'],
            'user_id': session['user_id'],
            'friend_id': request.form['friend_id']
        }
        Message.save_message(data)
        return redirect('/yourpage')


@app.route("/delete/<int:id>")                  #deletes a message
def delete_message(id):
    data = {
        "id":id
    }
    Message.delete_message(data)
    return redirect("/yourpage")


@app.route("/logout")                           #logs out the user / clears the session
def logout():
    session.clear()
    flash("logged out!", "login")
    return redirect("/")
