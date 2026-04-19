class User:
    def __init__(self, user_id, username, email, password=None, google_auth=False):
        if not email or "@" not in email:
            raise ValueError("A valid email is required.")
        if not username:
            raise ValueError("Username cannot be empty.")
        if not google_auth and not password:
            raise ValueError("Password is required for non-Google accounts.")
        
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.google_auth = google_auth

    @staticmethod
    def register(user_id, username, email, password):
         if not username:
            raise ValueError("Username cannot be empty.")
         if not email or "@" not in email:
            raise ValueError("Invalid email format.")
         if not password:
            raise ValueError("Password cannot be empty.")
         if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")
         return User(user_id, username, email, password)

    @staticmethod
    def google_login(user_id, username, email):
        if not email or "@" not in email:
            raise ValueError("Invalid Google account email.")
        return User(user_id, username, email, google_auth=True)

    def login(self, email, password):
        if self.google_auth:
            raise ValueError("This account uses Google login.")
        return self.email == email and self.password == password

    def __repr__(self):
        return f"User(id={self.user_id}, username={self.username}, email={self.email}, google={self.google_auth})"