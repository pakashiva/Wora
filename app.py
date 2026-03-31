from flask import Flask, render_template , redirect , url_for ,request, session , flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import random

app = Flask(__name__)


#image upload requirements
app.config['UPLOAD_FOLDER'] =  os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Temproary database
db = []
users = []

sample_usernames = ["alice", "bob", "charlie", "david", "eve"]
sample_passwords = ["pass123", "qwerty", "abc123", "secret", "letmein"]
sample_posts = [
    "Hello world!",
    "Testing my first post",
    "Flask is fun",
    "Random thoughts...",
    "Another day, another post"
]

# Create users
for i in range(len(sample_usernames)):
    temp = {
        'user_id': i + 1,
        'username': sample_usernames[i],
        'password': sample_passwords[i]
    }
    users.append(temp)

# Create posts linked to users
for i in range(10):  # 10 random posts
    user = random.choice(users)
    temp_dict = {
        'username': user['username'],
        'content': random.choice(sample_posts),
        'user_id': user['user_id']
    }
    db.append(temp_dict)

#session key
app.secret_key = 'ganiag'

# check-logge-in

def login_required(f):
    @wraps(f)
    def wrapper(*args , **kwargs):
        if "user_id" not in session:
            print("NOT LOGGED IN")
            return redirect(url_for('login'))
        return f(*args , **kwargs)
    return wrapper



@app.route('/')
def home():
    return render_template('index.html' , db = db, users = users)
    


# Add new post
@app.route('/add', methods = ['POST'])
@login_required
def add_msg():
    content = request.form.get('content')

    # 🔒 Always take user from session, not form
    user = next((u for u in users if u['user_id'] == session['user_id']), None)

    if user and content:
        temp_dict = {
            'username': user['username'],
            'content': content,
            'user_id': user['user_id']
        }
        db.append(temp_dict)
    return redirect(url_for('home'))
    
# Delete post
@app.route('/delete/<int:idx>')
@login_required
def del_post(idx):
    if 0 <= idx < len(db):
        if session['user_id'] == db[idx]['user_id']:
            db.pop(idx)
        else:
            return 'Unauthorised Access' , 403    
    return redirect(url_for('home'))
    
# update post
@app.route('/update/<int:idx>' , methods = ['GET' , 'POST'])
@login_required
def update_content(idx):
    if 0 <= idx < len(db):
        post = db[idx]

        if session['user_id'] != db[idx]['user_id']:
            return 'Unauthorised Access' , 403
            
        if request.method == 'POST':
            new_content = request.form.get('updated_content')

            if new_content:
                db[idx]['content'] = new_content
                return redirect(url_for('home'))

            
        return render_template(
                    'update.html', 
                    username = post['username'] , 
                    content = post['content'] , 
                    idx = idx)

    return 'Post not found' , 404    

    

   

# registration
@app.route('/register' , methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))

        # File handling

        file = request.files.get('photo')
        filename = None 

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        if username and password:
            temp = {
                'user_id': len(users) + 1,
                'username': username,
                'password': password,
                'profile': filename  
            }
            users.append(temp)
            
            return redirect(url_for('login'))
    
    return render_template('register.html')

# Authentication

@app.route('/login' , methods = ['GET' , 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        for user in users:
            if user['username'] == username and check_password_hash(user['password'] , password):
                session['user_id'] = user["user_id"]
                return redirect(url_for('home'))
            
        return 'Invalid Credentials'
    
    return render_template('login.html')

# logout

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    return redirect(url_for('login'))



# context processor
@app.context_processor
def inject_user():
    
    current_user = None

    if 'user_id' in session:
        for user in users:
            if user['user_id'] == session['user_id']:
                current_user = user
                break
    return dict(current_user = current_user)    
   


if __name__ == '__main__':
    app.run(debug=True)
