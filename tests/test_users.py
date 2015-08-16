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
        db.create_all()

    def tearDown(self):
        db.drop_all()
        pass

    def test_new_user(self):
        """
        Tests that a user is created and the data sent back matches what was passed in"
        """
        resp = self.app.post('/users', data=json.dumps(self.test_user1_data))
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data == self.test_user1_data

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

