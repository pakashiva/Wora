from flask import Flask, render_template , redirect , url_for ,request, session , flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#setting-up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_sql = SQLAlchemy(app)

# define models

class User(db_sql.Model):
    id = db_sql.Column(db_sql.Integer , primary_key = True)
    username = db_sql.Column(db_sql.String(100) , unique = True , nullable = False)
    password = db_sql.Column(db_sql.String(200) , nullable = False)
    profile = db_sql.Column(db_sql.String(200))

class Post(db_sql.Model):
    id = db_sql.Column(db_sql.Integer, primary_key = True)
    content = db_sql.Column(db_sql.Text ,nullable = False)
    user_id = db_sql.Column(db_sql.Integer , db_sql.ForeignKey('user.id') , nullable =  False)

    user = db_sql.relationship('User' , backref = 'posts')


#image upload requirements
app.config['UPLOAD_FOLDER'] =  os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



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


#home route

@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('index.html' , posts=posts)
    


# Add new post
@app.route('/add', methods = ['POST'])
@login_required
def add_msg():
    content = request.form.get('content')

    user = User.query.get(session['user_id'])


    if user and content:
        newpost = Post(content=content , user_id = user.id)
        db_sql.session.add(newpost)
        db_sql.session.commit()

    return redirect(url_for('home'))
    
# Delete post
@app.route('/delete/<int:idx>')
@login_required
def del_post(idx):

    post = Post.query.get(idx)

    if post and post.user_id == session['user_id']:
        db_sql.session.delete(post)
        db_sql.session.commit()
          
    return redirect(url_for('home'))
    
# update post
@app.route('/update/<int:idx>' , methods = ['GET' , 'POST'])
@login_required
def update_content(idx):
    
    if request.method == 'POST':
        new_content = request.form.get('updated_content')

        post = Post.query.get(idx)

        if post and post.user_id == session['user_id']:
            post.content = new_content
            db_sql.session.commit()

            
        return render_template(
            'update.html',
            username=post.user.username,
            content=post.content,
            idx=idx
        )

    return 'Post not found' , 404    

    

# registration
@app.route('/register' , methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        hashed_password = generate_password_hash(request.form.get('password'))

        # File handling

        file = request.files.get('photo')
        filename = None 

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        if username and hashed_password:
            new_user = User(username=username, password=hashed_password, profile=filename)
            db_sql.session.add(new_user)
            db_sql.session.commit()
            
            return redirect(url_for('login'))
    
    return render_template('register.html')

# Login

@app.route('/login' , methods = ['GET' , 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter(username=username).first()

        if user and check_password_hash(user.password , password):
            session['user_id'] = user.id
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
        user = User.query.get(session['user_id'])
        return dict(current_user = user)
    return dict(current_user = None)    
   


if __name__ == '__main__':
    app.run(debug=True)
