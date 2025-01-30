from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Get a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by their email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        # Construct a query to select the user with the specified email
        stmt = select(User).filter_by(email=email)
        
        # Execute the query asynchronously
        user = await self.db.execute(stmt)
        
        # Return the result, which is expected to be a single user or None
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user.

        Args:
            body (UserCreate): The user data to create.
            avatar (str, optional): The avatar URL. Defaults to None.

        Returns:
            User: The created user.
        """
        # Create a new User instance with the fields from body
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            # Set the hashed_password with the password from body
            hashed_password=body.password,
            # Set the avatar URL (if provided)
            avatar=avatar
        )
        # Add the user to the database
        self.db.add(user)
        # Commit the changes
        await self.db.commit()
        # Refresh the user object
        await self.db.refresh(user)
        # Return the created user
        return user
    
    async def confirmed_email(self, email: str) -> None:
        """
        Confirm the user's email by setting the confirmed status to True.

        Args:
            email (str): The email of the user to confirm.
        """
        # Retrieve the user by their email address
        user = await self.get_user_by_email(email)
        
        # Set the user's confirmed status to True
        user.confirmed = True
        
        # Commit the changes to the database
        await self.db.commit()
        
    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the user's avatar URL in the database.

        Args:
            email (str): The email of the user to update.
            url (str): The new avatar URL.

        Returns:
            User: The updated user.
        """
        # Retrieve the user by their email address
        user = await self.get_user_by_email(email)
        
        # Update the user's avatar URL
        user.avatar = url
        
        # Commit the changes to the database
        await self.db.commit()
        
        # Refresh the user object
        await self.db.refresh(user)
        
        # Return the updated user
        return user
