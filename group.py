from app import db


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    groupid = db.Column(db.String(32), unique=True)

    def __init__(self, groupid=None):
        self.groupid = groupid

    def __repr__(self):
        return '<Group {}>'.format(self.groupid)
