import unittest2 as unittest


from plone.login.testing import \
    PLONE_LOGIN_INTEGRATION_TESTING


class TestExample(unittest.TestCase):

    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        pass

    def test_success(self):
        sum = 1 + 3
        self.assertEqual(sum, 4)

