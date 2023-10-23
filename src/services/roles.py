from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User
from src.schemas.schemas import Role
from src.services.auth import auth_service


class RoleChecker:
    def __init__(self, allowed_roles: List[Role]):
        """
        The __init__ function is called when the class is instantiated.
            It sets up the instance of the class with a list of allowed roles.
        
        :param self: Represent the instance of the class
        :param allowed_roles: List[Role]: Define the allowed roles for a command
        :return: Nothing
        """
        
        self.allowed_roles = allowed_roles

    async def __call__(self,
                       request: Request,
                       current_user: User = Depends(auth_service.get_current_user)):
        """
        The __call__ function is the decorator that will be used to check if a user has the correct role.
            It takes in a request and current_user, which is passed from auth_service.get_current_user().
            If the current user's roles are not in self.allowed_roles, then an HTTPException with status code 403 
            (Forbidden) will be raised.
        
        :param self: Access the class attributes
        :param request: Request: Access the request object
        :param current_user: User: Get the current user from the auth_service
        :return: A function that takes in a request and current_user, which is the user returned from auth_service
        """
        if current_user.roles not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")