from app import db


user_groups = db.Table('usergroups',
    db.Column('userid', db.Integer, db.ForeignKey('users.id')),
    db.Column('groupid', db.Integer, db.ForeignKey('groups.id'))
)
