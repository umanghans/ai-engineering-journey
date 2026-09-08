USERS = {
    1: {"name": "Alice", "role": "admin"},
    2: {"name": "Bob", "role": "developer"},
}


def get_user(user_id: int):
    return USERS.get(user_id)