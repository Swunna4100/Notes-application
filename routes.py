from flask import render_template, request, redirect, url_for
from flask import Flask, flash
from flask_login import login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from models import User, Notes

def register_routes(app, db):

    @app.route("/")
    def home():
        return render_template("home.html", title="Home Page")

    @app.route("/add_note", methods=['GET', 'POST'])
    @login_required
    def add_note():
        if request.method == 'GET':
            return render_template("add.html", title="Add a note")
        elif request.method == 'POST':
            title = request.form['notetitle']
            content = request.form['notecontent']
            if title.strip() == "" or content.strip() == "":
                flash("Note Title/Content cannot be empty.")
                return render_template("add.html", title="Add a note")
            else:
                new_note = Notes(title=title, content=content, user_id=current_user.id)

            db.session.add(new_note)
            db.session.commit()

            flash('New note added!')  #fix this so that you cant add a new note that is empty

            return redirect(url_for('view_notes'))



    @app.route("/view_notes", methods=['GET', 'POST'])
    @login_required
    def view_notes():
        notes = Notes.query.filter_by(user_id=current_user.id).all()
        return render_template("notes.html", notes=notes,  title="View notes")
    

    @app.route("/Delete_note", methods=['POST'])
    @login_required
    def delete_notes():
        note_id = request.form.get('note_id')

        if not note_id:
            flash("Error: No note ID provided.")
            return redirect(url_for('view_notes'))

        note = Notes.query.get(note_id)

        if not note:
            flash("Error: Note does not exist.")
            return redirect(url_for('view_notes'))

        db.session.delete(note)
        db.session.commit()

        flash(f"Deleted note: {note.title}")
        return redirect(url_for('view_notes'))
    
    @app.route("/edit_note/<int:note_id>", methods=['GET','POST']) 
    @login_required
    def edit_note(note_id):
        #gets note from db for both get and post
        note = Notes.query.get(note_id)
        
        if not note:
            flash("Note not found!")
            return redirect(url_for('view_notes'))

        #show edit from
        if request.method == 'GET':
            return render_template("edit.html", note=note)

        #updates the db object using from data
        elif request.method == 'POST':
            note.title = request.form['note_title']
            note.content = request.form['note_content']

            db.session.commit()

            flash(f'Edited note: {note.title}')
            return redirect(url_for('view_notes'))


    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if not username or not password:
                flash("Username/Password cannot be empty")
                return redirect(url_for("register"))

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("User already exists")
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash(f"Account created, You are now logged in as: {username}")
            return redirect(url_for("home"))

        
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user = User.query.filter_by(username=username).first()

            if not user:
                flash("User does not exist.")
                return redirect(url_for("login"))

            if not check_password_hash(user.password, password):
                flash("Incorrect username/password.")
                return redirect(url_for("login"))

            login_user(user)
            flash(f"Welcome back, {username}")
            return redirect(url_for("home"))
    
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()  
        flash("You have been logged out.")
        return redirect(url_for("home"))



    


     

  