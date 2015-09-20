from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String())
    gd_access_token = db.Column(db.String())
    db_access_token = db.Column(db.String())
    files = db.relationship('File', backref = 'owner', lazy = 'joined')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r Password %r >' % (self.username, self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(), index = True)
    path = db.Column(db.String(), index = True, unique = True)
    dropbox = db.Column(db.Boolean())
    folder = db.Column(db.Boolean())
    last_modified = db.Column(db.DateTime())
    last_updated = db.Column(db.DateTime())

    def __repr__(self):
        return '<Post %r>' % (self.path)

    def __init__(self, owner_id, title, path, dropbox, folder, last_modified, last_updated = None):
        self.owner_id = owner_id
        self.title = title
        self.path = path
        self.dropbox = dropbox
        self.folder = folder
        self.last_modified = last_modified
        if last_updated is None:
            self.last_updated = datetime.now()


