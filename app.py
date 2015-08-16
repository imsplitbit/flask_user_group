#!/usr/bin/env python
import json
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    session,
    make_response,
    redirect,
    url_for,
    abort
)
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask('user_group_app')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

user_groups = db.Table('usergroups',
    db.Column('userid', db.Integer, db.ForeignKey('users.id')),
    db.Column('groupid', db.Integer, db.ForeignKey('groups.id')),
    db.PrimaryKeyConstraint('userid', 'groupid')
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    userid = db.Column(db.String(32), unique=True)
    groups = db.relationship('Group',
                             secondary=user_groups,
                             backref='users')

    def __init__(self, first_name=None, last_name=None, userid=None):
        self.first_name = first_name
        self.last_name = last_name
        self.userid = userid

    def __repr__(self):
        return '<User {}>'.format(self.userid)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    groupid = db.Column(db.String(32), unique=True)

    def __init__(self, groupid=None):
        self.groupid = groupid

    def __repr__(self):
        return '<Group {}>'.format(self.groupid)


@app.route('/users', methods=['POST'])
def new_user():
    user_data = json.loads(request.data)
    userid = user_data.get('userid')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    groupids = user_data.get('groups', [])

    # Validate user input
    if not (userid and first_name and last_name and groupids):
        # Required data doesn't exist, "Bad Request"
        abort(400)

    # Ensure groups is a list
    if not isinstance(groupids, list):
        # Groups is not a list, "Bad Request"
        abort(400)

    # Next see if we already have a user with this userid
    db_user = User.query.filter_by(userid=userid).first()
    if db_user:
        # We already have this user, return "Conflict"
        abort(409)

    # We have a new user but before we create that
    # we need to make sure the groups exist.
    db_groups = []
    for groupid in groupids:
        db_group = Group.query.filter_by(groupid=groupid).first()
        if not db_group:
            # Group doesn't exist so we need to create it
            db_group = Group(groupid=groupid)
            db.session.add(db_group)
            db.session.commit()

        db_groups.append(db_group)

    # Create a new user and save to the db
    db_user = User(first_name=first_name, last_name=last_name, userid=userid)
    for db_group in db_groups:
        db_user.groups.append(db_group)

    db.session.add(db_user)
    db.session.commit()

    # Build a result for the new user response
    return create_user_response(db_user)

@app.route('/users/<userid>', methods=['GET'])
def find_user(userid):
    # See if user exists
    db_user = User.query.filter_by(userid=userid).first()
    if not db_user:
        abort(404)

    return create_user_response(db_user)


@app.route('/users/<userid>', methods=['PUT'])
def modify_user(userid):
    pass


@app.route('/users/<userid>', methods=['DELETE'])
def delete_user(userid):
    pass


def create_user_response(db_user):
    result = {
        'first_name': db_user.first_name,
        'last_name': db_user.last_name,
        'userid': db_user.userid,
        'groups': [x.groupid for x in db_user.groups]
    }
    return make_response(jsonify(result), 200)

if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.run()
