from flask import Flask, render_template, redirect, request  # Core Flask imports for web app
from flask_scss import Scss  # Enables SCSS compilation for styling
from flask_sqlalchemy import SQLAlchemy  # Flask integration for SQLAlchemy ORM
from datetime import datetime  # Used for timestamps on tasks

app = Flask(__name__)
scss = Scss(app) # Initialize SCSS support with Flask

# Configure the SQLite database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the Flask app

# Define the Task model (database table structure)
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique task identifier
    content = db.Column(db.String(200), nullable=False)  # Task description (required)
    complete = db.Column(db.Boolean, default=False)  # Task completion flag
    created = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for task creation

    def __repr__(self) -> str:
        return f"Task{self.id}"  # Human-readable representation for debugging

# Home route: displays tasks & handles new task creation
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        current_task = request.form['content']  # Get the new task's content
        new_task = MyTask(content=current_task)  # Instantiate a new task object
        try:
            db.session.add(new_task)  # Stage the new task for insert
            db.session.commit()       # Persist it to the database
            return redirect("/")      # Refresh page after POST (Post/Redirect/Get pattern)
        except Exception as e:
            print(f"ERROR {e}")
            return f"ERROR {e}"
    else:
        # GET request: fetch all tasks, oldest first
        tasks = MyTask.query.order_by(MyTask.created).all()
        return render_template('index.html', tasks=tasks)

# Route to delete a task by its integer ID
@app.route("/delete/<int:id>")
def delete(id: int):
    delete_task = MyTask.query.get_or_404(id)  # Retrieve or return 404 if not found
    try:
        db.session.delete(delete_task)  # Stage deletion
        db.session.commit()             # Persist deletion
        return redirect("/")            # Redirect to homepage
    except Exception as e:
        return f"Error: {e}"

# Route to edit a task by its integer ID
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    task = MyTask.query.get_or_404(id)  # Retrieve task or 404

    if request.method == "POST":
        task.content = request.form['content']  # Update the task content
        try:
            db.session.commit()  # Save updates
            return redirect("/")  # Return to homepage
        except Exception as e:
            return f"Error: {e}"
    else:
         return render_template("edit.html", task=task)  # This could render an edit form instead

# Application entry point
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create DB tables if not already present

    app.run(debug=True)  # Start the app in debug mode for development
