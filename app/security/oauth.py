from fastapi.security import OAuth2PasswordBearer

# The tokenUrl points to our login endpoint which we'll implement under auth routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
