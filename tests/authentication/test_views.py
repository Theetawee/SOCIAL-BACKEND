from .test_setup import TestSetUp


class TestViews(TestSetUp):
    def test_login_view(self):
        response = self.client.post(self.login_url)

        self.assertEqual(response.status_code, 200)
