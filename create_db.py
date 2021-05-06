from flask_app import create_app,db
if __name__=='__main__':
    app=create_app()
    app.app_context().push()
    db.create_all()
    print("New Database created at",app.root_path)
