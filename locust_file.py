from locust import HttpLocust, TaskSet, task


class WebsiteTasks(TaskSet):
    def on_start(self):
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjE1Njc5NTY5ODEsImlhdCI6MTU2NzY5Nzc3Niwic3ViIjoyLCJ1c2VyIjp7ImlkIjoyLCJlbWFpbCI6Im50dWFuMjIxQGdtYWlsLmNvbSIsImlzX2NvbmZpcm1lZCI6dHJ1ZX0sInJvbGVfaWRzIjpbNl0sInBlcm1pc3Npb25zIjpbImFkbWluIl19.QGGD1t-nez8PkKQuNtHk5x7BJ-dfea__gQ92x0n5bzDrBnDwA5u8VMTF011wSAVi_o5Vb_17SAhxPmMQ4qxeyoAuSl1Ar5c_jPFaGH8VGcvtqu0Lp0F3drkQxmenncR4TyDvsVdhJmvk1lj0P6fkH5-wdaf7QPxkOiiC7od-B56cxR9jkUH9udDgPJ-Gzto7xqiutgpw68z8TJMNjTahsDnC6mvm16E_44U_l9jdANUP7fgy_NYrws7mbYrtfGmPfbozCe38sko5H4frhJB0lQWjyN7O1fmHllQ4dw2k4Ygy0FEBFqvz5naELSZTUIJ6X_bM32SCooSgsc2aZJOBuA"
        self.headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }

    @task
    def get_all_user(self):
        self.client.get("/admin/users", headers=self.headers)

    @task
    def get_current_user_profile(self):
        self.client.get("/users/profile", headers=self.headers)

    @task
    def get_one_user_profile(self):
        self.client.get("/admin/users/2/profile", headers=self.headers)


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000

# locust -f locustfile.py
# locust -f locust_files/my_locust_file.py --master --host=http://example.com
