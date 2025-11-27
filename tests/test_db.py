import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.db import get_db




@pytest.mark.asyncio
async def test_raw_session_works():
    # Directly test get_db dependency logic
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
        break  # exit after first yield
