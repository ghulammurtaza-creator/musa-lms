import asyncio
from app.core.database import get_db_session
from sqlalchemy import select
from app.models.models import Teacher

async def main():
    async with get_db_session() as db:
        result = await db.execute(select(Teacher))
        teachers = result.scalars().all()
        
        if teachers:
            print('Teachers in database:')
            for t in teachers:
                print(f'  - {t.email} (ID: {t.id}, Name: {t.name})')
        else:
            print('No teachers found in database')

if __name__ == "__main__":
    asyncio.run(main())
