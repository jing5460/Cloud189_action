class UserInfo:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.nickName = None

        self.sessionKey = None
        self.sessionSecret = None
        self.eAccessToken = None
        self.familySessionKey = None
        self.familySessionSecret = None
