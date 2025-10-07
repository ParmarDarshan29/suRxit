from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import uuid
import os

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthManager:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        
        # Mock user storage (replace with database in production)
        self.users_db = {
            "doctor@example.com": {
                "id": "doc_001",
                "email": "doctor@example.com",
                "hashed_password": self.hash_password("password"),
                "name": "Dr. Sarah Smith",
                "role": "doctor",
                "is_active": True,
                "created_at": datetime.now()
            },
            "admin@surxit.com": {
                "id": "admin_001", 
                "email": "admin@surxit.com",
                "hashed_password": self.hash_password("admin123"),
                "name": "System Administrator",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.now()
            }
        }

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            
            if email is None:
                raise JWTError("Token missing subject")
            
            # In production, fetch user from database
            user = self.users_db.get(email)
            if user is None:
                raise JWTError("User not found")
            
            if not user["is_active"]:
                raise JWTError("User account is disabled")
            
            return {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
            
        except JWTError as e:
            raise Exception(f"Token validation failed: {str(e)}")

    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        user = self.users_db.get(email)
        
        if not user:
            raise Exception("Invalid credentials")
        
        if not self.verify_password(password, user["hashed_password"]):
            raise Exception("Invalid credentials")
        
        if not user["is_active"]:
            raise Exception("Account is disabled")
        
        # Create access token
        access_token = self.create_access_token(
            data={"sub": user["email"], "role": user["role"]}
        )
        
        # Update last login
        user["last_login"] = datetime.now()
        
        return {
            "token": access_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        }

    async def create_user(self, email: str, password: str, name: str, role: str = "doctor") -> Dict[str, Any]:
        """Create a new user account"""
        # Check if user already exists
        if email in self.users_db:
            raise Exception("User already exists")
        
        # Validate role
        if role not in ["doctor", "admin", "patient"]:
            raise Exception("Invalid role")
        
        # Create new user
        user_id = f"{role}_{str(uuid.uuid4())[:8]}"
        hashed_password = self.hash_password(password)
        
        new_user = {
            "id": user_id,
            "email": email,
            "hashed_password": hashed_password,
            "name": name,
            "role": role,
            "is_active": True,
            "created_at": datetime.now()
        }
        
        # Store user (in production, save to database)
        self.users_db[email] = new_user
        
        return {
            "id": user_id,
            "email": email,
            "name": name,
            "role": role
        }

    async def change_password(self, user_email: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.users_db.get(user_email)
        
        if not user:
            raise Exception("User not found")
        
        if not self.verify_password(old_password, user["hashed_password"]):
            raise Exception("Current password is incorrect")
        
        # Update password
        user["hashed_password"] = self.hash_password(new_password)
        return True

    async def reset_password(self, email: str) -> str:
        """Generate password reset token"""
        user = self.users_db.get(email)
        
        if not user:
            raise Exception("User not found")
        
        # Create reset token (expires in 15 minutes)
        reset_token = self.create_access_token(
            data={"sub": email, "type": "password_reset"}
        )
        
        # In production, send email with reset link
        return reset_token

    async def verify_reset_token(self, token: str, new_password: str) -> bool:
        """Verify reset token and update password"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if email is None or token_type != "password_reset":
                raise JWTError("Invalid reset token")
            
            user = self.users_db.get(email)
            if not user:
                raise JWTError("User not found")
            
            # Update password
            user["hashed_password"] = self.hash_password(new_password)
            return True
            
        except JWTError:
            raise Exception("Invalid or expired reset token")

    def get_user_permissions(self, role: str) -> List[str]:
        """Get user permissions based on role"""
        permissions = {
            "admin": [
                "read:all", "write:all", "delete:all",
                "manage:users", "manage:system"
            ],
            "doctor": [
                "read:patients", "write:prescriptions", "read:analytics",
                "chat:medlm", "analyze:prescriptions"
            ],
            "patient": [
                "read:own_data", "chat:medlm", "view:recommendations"
            ]
        }
        return permissions.get(role, [])

    async def check_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """Check if user has specific permission"""
        user_permissions = self.get_user_permissions(user["role"])
        return permission in user_permissions