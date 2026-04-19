class Admin:
    def __init__(self, admin_id):
        self.admin_id = admin_id

    def manage_user_accounts(self, users_list, action, target_user_id):
        if action == "view":
            result = [u for u in users_list if u.user_id == target_user_id]
            if not result:
                raise ValueError(f"User {target_user_id} not found.")
            return result[0]
        elif action == "delete":
            updated = [u for u in users_list if u.user_id != target_user_id]
            if len(updated) == len(users_list):
                raise ValueError(f"User {target_user_id} not found.")
            return updated
        else:
            raise ValueError(f"Unknown action: '{action}'. Must be 'view' or 'delete'.")

    def __repr__(self):
        return f"Admin(id={self.admin_id})"