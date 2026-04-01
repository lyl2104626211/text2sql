import asyncio
from typing import Optional

from app.config.app_config import DBConfig, app_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy import text


class MysqlClientManager:
    def __init__(self, config: DBConfig):
        self.config = config
        self.engine: Optional[AsyncEngine] = None
        self.session_factory = None

    def _geturl(self) -> str:
        return (f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/"
                f"{self.config.database}?charset=utf8mb4")

    def init(self):
        self.engine = create_async_engine(url=self._geturl(),
                                          pool_size=10,
                                          pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine,
                                                  autoflush=True,
                                                  expire_on_commit=False,
                                                  autobegin=True)

    async def close(self):
        await self.engine.dispose()


db_meta_manager = MysqlClientManager(config=app_config.db_meta)
db_dw_manager = MysqlClientManager(config=app_config.db_dw)



if __name__ == '__main__':
    dw_manager.init()


    async def test():
        async with dw_manager.session_factory() as session:
            result = await session.execute(text("select * from table_info limit 10"))
            rows = result.fetchall()
            print(rows)


    asyncio.run(test())
