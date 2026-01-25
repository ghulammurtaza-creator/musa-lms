#!/bin/sh
set -e

echo "🚀 Starting Academy Management System Backend on Fly.io..."

# Database should already be ready (Fly.io managed Postgres)
echo "⏳ Waiting for database connection..."
sleep 3

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head

# Check if admin user should be created
if [ "$CREATE_ADMIN" = "true" ]; then
    echo "👤 Creating admin user..."
    python -c "
import sys
import asyncio
sys.path.insert(0, '.')
from app.core.database import AsyncSessionLocal
from app.models.models import AuthUser, AuthUserRole
from app.core.security import get_password_hash
from sqlalchemy import select
import os

async def create_admin():
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin already exists
            result = await db.execute(
                select(AuthUser).filter(AuthUser.role == AuthUserRole.ADMIN)
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print(f'ℹ️  Admin user already exists: {existing_admin.email}')
            else:
                # Get credentials from environment
                admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
                admin_password = os.getenv('ADMIN_PASSWORD')
                admin_name = os.getenv('ADMIN_NAME', 'System Administrator')
                
                if not admin_password:
                    print('⚠️  ADMIN_PASSWORD not set, skipping admin creation')
                    return
                
                # Create admin user
                admin = AuthUser(
                    email=admin_email,
                    hashed_password=get_password_hash(admin_password),
                    full_name=admin_name,
                    role=AuthUserRole.ADMIN,
                    is_active=True
                )
                db.add(admin)
                await db.commit()
                print(f'✅ Admin user created: {admin_email}')
                print(f'   Password: {admin_password}')
                print(f'   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!')
        except Exception as e:
            print(f'❌ Error creating admin: {e}')
            import traceback
            traceback.print_exc()

# Run the async function
asyncio.run(create_admin())
"
fi

echo "🌐 Starting Uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
