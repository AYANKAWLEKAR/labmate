"""
Prisma database client for Python backend.
"""
from pathlib import Path
from prisma import Prisma
import asyncio

# Global Prisma client instance
prisma: Prisma = None
_connection_lock = asyncio.Lock()



#prisma schema?
async def get_prisma() -> Prisma:
    """Get or create Prisma client instance."""
    global prisma
    if prisma is not None and prisma.is_connected():
        return prisma

    async with _connection_lock:
        if prisma is not None and prisma.is_connected():
            return prisma
        elif prisma is None:
            # Get the schema path relative to the database folder
            # Assuming we're in backend/app/db.py, go up to find database folder
            try:
                current_dir = Path(__file__).parent.parent.parent
                schema_path = current_dir / "database" / "prisma" / "schema.prisma"
                
                prisma = Prisma(
                    schema_path=str(schema_path) if schema_path.exists() else None
                )
                await prisma.connect()
            except Exception as e:
                print(f"Error connecting to database: {e}")
                raise e
   
    return prisma


async def close_prisma():
    """Close Prisma client connection."""
    global prisma
    if prisma is not None:
        await prisma.disconnect()
        prisma = None
