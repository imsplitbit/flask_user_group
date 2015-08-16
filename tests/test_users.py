import app
import unittest
import json
from copy import deepcopy
from app import db


class UserTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.test_group1_groupid = 'admins'
        self.test_group2_groupid = 'users'
        self.test_user1_first = 'Peter'
        self.test_user1_last = 'Parker'
        self.test_user1_userid = 'spiderman'
        self.test_user1_groups = [self.test_group1_groupid, self.test_group2_groupid]
        self.test_user2_first = 'Wade'
        self.test_user2_last = 'Wilson'
        self.test_user2_userid = 'deadpool'
        self.test_user2_groups = [self.test_group2_groupid]
        self.app = app.app.test_client()
        self.test_user1_data = {
            'first_name': self.test_user1_first,
            'last_name': self.test_user1_last,
            'userid': self.test_user1_userid,
            'groups': self.test_user1_groups
        }
        self.test_user2_data = {
            'first_name': self.test_user2_first,
            'last_name': self.test_user2_last,
            'userid': self.test_user2_userid,
            'groups': self.test_user2_groups
        }
        self.test_group1_data = [self.test_user1_userid]
        self.test_group1_modify = [self.test_user1_userid, self.test_user2_userid]
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def test_new_user(self):
        """
        Tests that a user is created and the data sent back matches what was passed in"
        """
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        assert resp.status_code == 200
        data = json.loads(resp.data)
        for key in ['first_name', 'last_name', 'userid', 'groups']:
            assert key in data
        assert data['first_name'] == self.test_user1_first
        assert data['last_name'] == self.test_user1_last
        assert data['userid'] == self.test_user1_userid
        for groupid in self.test_user1_groups:
            assert groupid in data['groups']

    def test_new_user_409(self):
        """
        Tests that a duplicate user creation attempt results in a 409
        """
        resp = self.app.post('/users', data=json.dumps(self.test_user2_data))
        assert resp.status_code == 200
        resp2 = self.app.post('/users', data=json.dumps(self.test_user2_data))
        assert resp2.status_code == 409

    def test_new_user_400(self):
        """
        Tests that missing any one key from the user data posted fails with 400
        """
        # Missing First Name
        user1_body = deepcopy(self.test_user1_data)
        del(user1_body['first_name'])
        resp = self.app.post('/users', data=json.dumps(user1_body))
        assert resp.status_code == 400

        # Missing Last Name
        user1_body = deepcopy(self.test_user1_data)
        del(user1_body['last_name'])
        resp = self.app.post('/users', data=json.dumps(user1_body))
        assert resp.status_code == 400

        # Missing UserID
        user1_body = deepcopy(self.test_user1_data)
        del(user1_body['userid'])
        resp = self.app.post('/users', data=json.dumps(user1_body))
        assert resp.status_code == 400

        # Bad data type for groups
        user1_body = deepcopy(self.test_user1_data)
        user1_body['groups'] = self.test_group1_groupid
        resp = self.app.post('/users', data=json.dumps(user1_body))
        assert resp.status_code == 400

    def test_get_user_exists(self):
        """
        Tests that once a user is created a subsequent get on that user returns valid user data.
        """
        # First make the user
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        assert resp.status_code == 200

        # Now get the user data and verify it is correct
        resp = self.app.get('/users/{}'.format(self.test_user1_userid))
        assert resp.status_code == 200
        data = json.loads(resp.data)
        for key in ['first_name', 'last_name', 'userid', 'groups']:
            assert key in data
        assert data['first_name'] == self.test_user1_first
        assert data['last_name'] == self.test_user1_last
        assert data['userid'] == self.test_user1_userid
        for groupid in self.test_user1_groups:
            assert groupid in data['groups']

    def test_get_user_404(self):
        """
        Tests that a user that doesn't exist returns a 404
        """
        resp = self.app.get('/users/thisuserdoesntexist')
        assert resp.status_code == 404

    def test_modify_userid_existing_user(self):
        """
        Tests that an existing user can be modified to change their userid
        """
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        assert resp.status_code == 200

        # Now modify the user's userid
        new_userid = u'venom'
        new_first = u'Eddie'
        new_last = u'Brock'
        new_groups = [u'villains']
        new_body = {
            'first_name': new_first,
            'last_name': new_last,
            'userid': new_userid,
            'groups': new_groups
        }
        resp = self.app.put('/users/{}'.format(self.test_user1_userid), data=json.dumps(new_body))
        assert resp.status_code == 200

        data = json.loads(resp.data)
        for key in ['first_name', 'last_name', 'userid', 'groups']:
            assert key in data
        assert data['first_name'] == new_first
        assert data['last_name'] == new_last
        assert data['userid'] == new_userid
        assert new_groups == data['groups']

        # Verify when we get the new userid things work
        resp = self.app.get('/users/{}'.format(new_userid))
        assert resp.status_code == 200

        data = json.loads(resp.data)
        for key in ['first_name', 'last_name', 'userid', 'groups']:
            assert key in data
        assert data['first_name'] == new_first
        assert data['last_name'] == new_last
        assert data['userid'] == new_userid
        assert new_groups == data['groups']

    def test_modify_userid_404(self):
        """
        Tests that when trying to modify a non-existent user we get a 404
        """
        resp = self.app.put('/users/thisuserdoesntexist',
                            data=json.dumps(self.test_user1_data))
        assert resp.status_code == 404

    def test_delete_user_404(self):
        """
        Tests that we get a 404 when deleting a non-existent user
        """
        resp = self.app.delete('/users/thisuserdoesntexist')
        assert resp.status_code == 404

    def test_delete_user(self):
        """
        Deletes a user and verifies it is deleted.
        """
        # First create a user to delete
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        assert resp.status_code == 200

        # Now delete it
        resp = self.app.delete('/users/{}'.format(self.test_user1_userid))
        assert resp.status_code == 200

        # Finally check to make sure it's not in the db
        resp = self.app.get('/users/{}'.format(self.test_user1_userid))
        assert resp.status_code == 404

    def test_list_group_by_id(self):
        """
        Add 2 users and then get a list of the group and validate that the users id's are listed.
        """
        # First add our users
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        assert resp.status_code == 200

        resp = self.app.post('/users', data=json.dumps(self.test_user2_data))
        assert resp.status_code == 200

        # Finally list the group
        resp = self.app.get('/groups/{}'.format(self.test_group2_groupid))
        assert resp.status_code == 200

        data = json.loads(resp.data)
        assert self.test_user1_userid in data
        assert self.test_user2_userid in data

    def test_list_group_404(self):
        """
        List a group that doesn't exist and verify we get a 404
        """
        resp = self.app.get('/groups/thisgroupdoesntexist')
        assert resp.status_code == 404

    def test_delete_group_404(self):
        """
        Attempt to delete a non-existent group and verify we get a 404
        """
        resp = self.app.delete('/groups/thisgroupdoesntexist')
        assert resp.status_code == 404

    def test_delete_group_by_id(self):
        """
        Create a user and delete one of it's groups
        """
        # Create a user with 2 groups
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        assert resp.status_code == 200

        # Delete one of those groups
        resp = self.app.delete('/groups/{}'.format(self.test_group1_groupid))
        assert resp.status_code == 200

        # Verify that the group is gone
        resp = self.app.get('/groups/{}'.format(self.test_group1_groupid))
        assert resp.status_code == 404

        # Verify that the user's groups don't have that group listed
        resp = self.app.get('/users/{}'.format(self.test_user1_userid))
        assert resp.status_code == 200

        data = json.loads(resp.data)
        assert self.test_group1_groupid not in data['groups']

    def test_modify_group_404(self):
        """
        Test that modifying a non-existent group results in a 404
        """
        resp = self.app.put('/groups/thisgroupdoesntexist',
                            data=json.dumps(self.test_group1_data))
        assert resp.status_code == 404

    def test_modify_group(self):
        """
        Add 2 users and then modify one group to add the missing user
        """
        # Add users
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        assert resp.status_code == 200

        resp = self.app.post('/users', data=json.dumps(self.test_user2_data))
        assert resp.status_code == 200

        # Modify group 1 to add user 2
        resp = self.app.put('/groups/{}'.format(self.test_group1_groupid),
                            data=json.dumps(self.test_group1_modify))
        assert resp.status_code == 200

        data = json.loads(resp.data)
        assert self.test_user1_userid in data
        assert self.test_user2_userid in data

        # Check user2 to see if it has group1 listed
        resp = self.app.get('/users/{}'.format(self.test_user2_userid))
        assert resp.status_code == 200

        data = json.loads(resp.data)
        assert 'groups' in data
        assert self.test_group1_groupid in data['groups']

    def test_create_group_409(self):
        """
        Test creating a group that already exists returns a 409
        """
        request = {
            'name': self.test_group1_groupid
        }
        # First create a group indirectly by making a user with a group
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        assert resp.status_code == 200

        # Now create a group that is already there
        resp = self.app.post('/groups', data=json.dumps(request))
        assert resp.status_code == 409

    def test_create_group_400(self):
        """
        Test that basic validation works and we get a 400
        """
        # No name key in request body
        resp = self.app.post('/groups', data=json.dumps({'nmae':self.test_group1_groupid}))
        assert resp.status_code == 400

        # Name isn't a unicode string
        resp = self.app.post('/groups', data=json.dumps({'name':10239}))
        assert resp.status_code == 400

    def test_create_group(self):
        """
        Test creating a new group
        """
        groupid = 'villains'

        # create the group
        resp = self.app.post('/groups', data=json.dumps({'name':groupid}))
        assert resp.status_code == 200

        # Fetch the group to check that it persists
        resp = self.app.get('/groups/{}'.format(groupid))
        assert resp.status_code == 200
