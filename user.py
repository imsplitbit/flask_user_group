from app import db
from usergroups import user_groups


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    userid = db.Column(db.String(32), unique=True)
    groups = db.relationship('Group',
                             secondary=user_groups,
                             backref=db.backref('users', lazy='dynamic'))

    def __init__(self, first_name=None, last_name=None, userid=None):
        self.first_name = first_name
        self.last_name = last_name
        self.userid = userid

    def __repr__(self):
        return '<User {}>'.format(self.userid)
