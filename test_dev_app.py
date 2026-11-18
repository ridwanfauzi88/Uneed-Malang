import unittest

from helpers import csrf_of, load_app, tmpdir
from shared import dss

M = load_app("app_dev", "website_dev/app_dev.py", {"DEV_ADMIN_PASSWORD": "tes-rahasia-1", "DEV_SECRET_KEY": "d" * 40})


class DevAppTests(unittest.TestCase):
    def setUp(self):
        self._old = dss.CONFIG_PATH
        dss.CONFIG_PATH = tmpdir() / "cfg.json"
        dss._cfg_cache.update(mtime=None, cfg=None)
        M._attempts.clear()
        self.c = M.app.test_client()

    def tearDown(self):
        dss.CONFIG_PATH = self._old
        dss._cfg_cache.update(mtime=None, cfg=None)

    def login(self, pw="tes-rahasia-1"):
        t = csrf_of(self.c.get("/dev/login").get_data(as_text=True))
        return self.c.post("/dev/login", data={"csrf_token": t, "password": pw})

    def test_admin_routes_require_login(self):
        for p in ("/dev/dashboard", "/dev/dss-config"):
            self.assertEqual(self.c.get(p).status_code, 302, p)
        r = self.c.post("/dev/dss-config", data={"m": "1"})
        self.assertIn(r.status_code, (302, 400))
        self.assertFalse(dss.CONFIG_PATH.exists())

    def test_default_password_rejected(self):
        self.assertEqual(self.login("admin123").status_code, 401)
        self.assertEqual(self.c.get("/dev/dashboard").status_code, 302)

    def test_login_and_pages(self):
        self.assertEqual(self.login().status_code, 302)
        for p in ("/dev/dashboard", "/dev/dss-config", "/dev/dss-config?cat=klinik", "/dev/dss-config?cat=ngawur"):
            self.assertEqual(self.c.get(p).status_code, 200, p)
        html = self.c.get("/dev/dashboard").get_data(as_text=True)
        self.assertNotIn("142", html)                 # metrik simulasi lama sudah dihapus

    def test_config_save_validation_and_effect(self):
        self.login()
        t = csrf_of(self.c.get("/dev/dss-config").get_data(as_text=True))
        base = {"csrf_token": t, "m": "8", "c": "4.0", "c_mode": "manual", "default_review_count": "10",
                "w_price": "50", "w_dist": "25", "w_rating": "25", "campus_name": "UB", "campus_lat": "-7.95", "campus_lng": "112.61"}
        for override in ({"w_rating": "40"}, {"m": "-1"}, {"c": "9"}, {"m": "nan"}, {"campus_lat": "999"}, {"c_mode": "x"}):
            r = self.c.post("/dev/dss-config", data={**base, **override})
            self.assertEqual(r.status_code, 200, override)
            self.assertFalse(dss.CONFIG_PATH.exists(), override)
        r = self.c.post("/dev/dss-config", data=base)
        self.assertEqual(r.status_code, 302)
        cfg = dss.load_config()
        self.assertEqual((cfg["bayesian_m"], cfg["weights"]["price"]), (8.0, 50.0))   # dibaca oleh sisi pengguna

    def test_logout_requires_post_and_csrf(self):
        self.login()
        self.assertEqual(self.c.get("/dev/logout").status_code, 405)
        t = csrf_of(self.c.get("/dev/dashboard").get_data(as_text=True))
        self.c.post("/dev/logout", data={"csrf_token": t})
        self.assertEqual(self.c.get("/dev/dashboard").status_code, 302)

    def test_login_rate_limit(self):
        for _ in range(5):
            self.login("salah")
        self.assertEqual(self.login().status_code, 429)


if __name__ == "__main__":
    unittest.main()
