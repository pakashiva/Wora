from app import app, db_sql, Post

with app.app_context():
    posts = Post.query.all()
    
    for p in posts:
        print(p.id, p.content, p.user_id)