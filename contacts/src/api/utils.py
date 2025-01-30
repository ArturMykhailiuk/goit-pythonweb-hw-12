from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Perform a health check on the database connection.

    This endpoint attempts to execute a simple query against the database
    to verify that the database is reachable and correctly configured.

    Parameters:
    - db: Database session dependency.

    Returns:
    - A success message if the database is reachable.

    Raises:
    - HTTPException: If there is an error connecting to the database or
      if the database is not correctly configured.
    """
    try:
        # Execute an asynchronous query to check database connectivity
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        # Raise an exception if the query result is None
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )

        # Return a success message if the database is reachable
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        # Log the exception and raise an HTTP error if there is a connection issue
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
