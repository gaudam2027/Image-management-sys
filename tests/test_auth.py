import pytest
from fastapi import HTTPException
from unittest.mock import patch
from services.auth_service import login_user,signup_user

class DummyUser :
    def __init__(self, email, password, is_blocked=False):
        self.email = email
        self.password = password
        self.is_blocked = is_blocked
        self.id = 1
        
class DummyDB:
    def __init__(self, user=None):
        self.user = user
        self.added  = None
    def query(self, model):
        return self
    def filter(self, *args):
        return self
    def first(self):
        return self.user
    def add(self, obj):    
        self.added = obj
    def commit(self):          
        pass
    def refresh(self, user):
        pass 
    
    
class DummyData:
    def __init__(self, email, password, name="test"):
        self.email = email
        self.password = password
        self.name = name
    
def test_login_invalid_email():
    db = DummyDB(user=None)
    data = DummyData("wrong@gmail.com", "123")

    with pytest.raises(HTTPException) as exc:
        login_user(db, data)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Invalid email"
    
def test_login_wrong_password():
    user = DummyUser("test@gmail.com", "hashed")
    db = DummyDB(user=user)
    data = DummyData("test@gmail.com", "wrong")

    with patch("services.auth_service.verify_password", return_value=False):
        with pytest.raises(HTTPException) as exc:
            login_user(db, data)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid password"
    
def test_login_blocked_user():
    user = DummyUser("test@gmail.com", "hashed", is_blocked=True)
    db = DummyDB(user=user)
    data = DummyData("test@gmail.com", "123")

    with patch("services.auth_service.verify_password", return_value=True):
        with pytest.raises(HTTPException) as exc:
            login_user(db, data)

    assert exc.value.status_code == 403
    assert exc.value.detail == "User is blocked"
    
def test_login_success():
    user = DummyUser("test@gmail.com", "hashed")
    db = DummyDB(user=user)
    data = DummyData("test@gmail.com", "123")

    with patch("services.auth_service.verify_password", return_value=True):
        with patch("services.auth_service.create_access_token", return_value="fake_token"):
            result = login_user(db, data)

    assert result["access_token"] == "fake_token"
    assert result["token_type"] == "bearer"
    
    
# ------------------------------signUp-----------------------------
    
def test_signup_existing_email():
    user = DummyUser("test@gmail.com", "hashed")
    db = DummyDB(user=user)
    data = DummyData("test@gmail.com", "123")

    with pytest.raises(HTTPException) as exc:
        signup_user(db, data)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Email already exists"
    

def test_signup_success():
    db = DummyDB(user=None)
    data = DummyData("new@gmail.com", "123")

    with patch("services.auth_service.hash_password", return_value="hashed_password"):
        result = signup_user(db, data)

    assert result["message"] == "User created"
    assert db.added is not None