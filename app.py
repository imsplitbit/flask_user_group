#!/usr/bin/env python
import json
from flask import (
    Flask,
    jsonify,
    request,
    make_response,
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
    user_data = validate_user_data(request.data)
    userid = user_data.get('userid')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    groupids = user_data.get('groups', [])

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
    # See if user exists
    db_user = User.query.filter_by(userid=userid).first()
    if not db_user:
        abort(404)

    user_data = validate_user_data(request.data)
    userid = user_data.get('userid')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    groupids = user_data.get('groups', [])

    db_user.userid = userid
    db_user.first_name = first_name
    db_user.last_name = last_name

    # This is a little tricky, I'll assume that you
    # need to send all the groups a user belongs
    # to and if the group isn't present in the
    # request body then it is deleted, otherwise
    # it's added.

    # Remove any groups that are associated with the user
    # that weren't sent in the request body.

    # for group in db_user.groups:
    #     if group.groupid not in groupids:
    #         db_user.groups.remove(group)
    # TODO(imsplitbit): For some reason even though the for loop
    # above should iterate over all groups for
    # a user it's not actually doing it.  It gets the first group
    # and deletes it and then moves on.  I'm doing a while loop to
    # just delete all groups and then add the user back to groups
    # passed in the request body.  This is not ideal but I didn't
    # want to burn too much time on this one problem.  The initial
    # idea was to remove only groups that were in the db for the user
    # that wasn't in the submitted groups in the request body.

    while len(db_user.groups) > 0:
        for group in db_user.groups:
            db_user.groups.remove(group)

    # Add groups from the request body that aren't in there
    # already.
    for groupid in groupids:
        if groupid not in [x.groupid for x in db_user.groups]:
            db_group = Group.query.filter_by(groupid=groupid).first()
            if not db_group:
                db_group = Group(groupid=groupid)
                db.session.add(db_group)
                db.session.commit()

            db_user.groups.append(db_group)

    db.session.add(db_user)
    db.session.commit()

    return create_user_response(db_user)


@app.route('/users/<userid>', methods=['DELETE'])
def delete_user(userid):
    # See if user exists
    db_user = User.query.filter_by(userid=userid).first()
    if not db_user:
        abort(404)

    db.session.delete(db_user)
    db.session.commit()

    return make_response('', 200)


@app.route('/groups/<groupid>', methods=['GET'])
def list_group(groupid):
    # See if the group exists
    db_group = Group.query.filter_by(groupid=groupid).first()
    if not db_group:
        abort(404)

    result = [x.userid for x in db_group.users]
    return make_response(json.dumps(result), 200)


@app.route('/groups/<groupid>', methods=['DELETE'])
def delete_group(groupid):
    # See if the group exists
    db_group = Group.query.filter_by(groupid=groupid).first()
    if not db_group:
        abort(404)

    db.session.delete(db_group)
    db.session.commit()

    return make_response('', 200)


@app.route('/groups/<groupid>', methods=['PUT'])
def modify_group(groupid):
    # See if the group exists
    db_group = Group.query.filter_by(groupid=groupid).first()
    if not db_group:
        abort(404)

    users = json.loads(request.data)
    for user in db_group.users:
        if user.userid not in users:
            db_group.users.remove(user)

    for userid in users:
        if userid not in [x.userid for x in db_group.users]:
            db_user = User.query.filter_by(userid=userid).first()
            if db_user:
                db_group.users.append(db_user)

    db.session.add(db_group)
    db.session.commit()

    return make_response(json.dumps([x.userid for x in db_group.users]), 200)


@app.route('/groups', methods=['POST'])
def add_group():
    data = json.loads(request.data)

    # Do some basic validation
    if 'name' not in data:
        abort(400)

    if not isinstance(data['name'], unicode):
        abort(400)

    groupid = data.get('name')

    # See if the group exists already
    db_group = Group.query.filter_by(groupid=groupid).first()
    if db_group:
        abort(409)

    db_group = Group(groupid=groupid)
    db.session.add(db_group)
    db.session.commit()

    result = [x.userid for x in db_group.users]
    return make_response(json.dumps(result), 200)


def create_user_response(db_user):
    result = {
        'first_name': db_user.first_name,
        'last_name': db_user.last_name,
        'userid': db_user.userid,
        'groups': [x.groupid for x in db_user.groups]
    }
    return make_response(jsonify(result), 200)


def validate_user_data(user_data):
    """
    Used to ensure all user related input is valid and returns
    an HTTP Status Code of 400 ("Bad Request") if any validation
    fails.

    :param user_data: raw json request data
    :return: dict of deserialized json request data
    """
    user_data = json.loads(user_data)
    userid = user_data.get('userid')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    groupids = user_data.get('groups', [])

    # Validate user input
    if not (userid and first_name and last_name and groupids):
        # Required data doesn't exist, "Bad Request"
        abort(400)

    if not (isinstance(userid, unicode) and
            isinstance(first_name, unicode) and
            isinstance(last_name, unicode)):
        # Userid, first_name or last_name isn't a
        # unicode string, "Bad Request"
        abort(400)

    # Ensure groups is a list
    if not isinstance(groupids, list):
        # Groups is not a list, "Bad Request"
        abort(400)

    for groupid in groupids:
        if not isinstance(groupid, unicode):
            # GroupID isn't a unicode sting, "Bad Request"
            abort(400)

    return user_data

if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.run(host='0.0.0.0')
