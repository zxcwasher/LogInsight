import asyncio
from models.helper import db
from models.analysis import Analysis
from models.incident import Severity
from utils.pattern_data import DEFAULT_PATTERNS
from datetime import datetime
now = datetime.utcnow()


async def seed_patterns():
    async with db.new_session() as session:
        for item in DEFAULT_PATTERNS:
            pattern = Analysis(
                key=item["key"],
                pattern=item["pattern"],
                severity=item["severity"],
                message=item["message"],
                category=item["category"],
                service=item.get("service"),
                enabled=item.get("enabled", True),
                priority=item.get("priority", 0),
                created_at=now,
                updated_at=now,
            )
            session.add(pattern)

        await session.commit()
        print("Patterns seeded")


if __name__ == "__main__":
    asyncio.run(seed_patterns())