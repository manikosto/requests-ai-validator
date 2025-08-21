import os


class Endpoints:

    list_all_users = "/users"
    delete_user_by_id = lambda self, user_id: f"/users/{user_id}"
    create_user = "https://dev-gs.qa-playground.com/api/v1/users"