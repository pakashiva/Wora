from app import app , db_sql

with app.app_context():
    db_sql.create_all()
    print('Database Created')