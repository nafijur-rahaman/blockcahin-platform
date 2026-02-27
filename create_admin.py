from app import app, db
from models import User

def create_admin():
    with app.app_context():
        print("--- Create Admin Account ---")
        email = input("Enter admin email: ")
        password = input("Enter admin password: ")

        # Check if this email is already registered
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            print(f"\nUser {email} already exists! Promoting them to Admin...")
            existing_user.is_admin = True
            db.session.commit()
            print("Success! User is now an Admin.")
        else:
            print(f"\nCreating brand new admin account for {email}...")
            new_admin = User(email=email, is_admin=True)
            new_admin.set_password(password)
            db.session.add(new_admin)
            db.session.commit()
            print("Success! New admin account created.")

if __name__ == '__main__':
    create_admin()