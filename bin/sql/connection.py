from sqlalchemy.ext.asyncio import create_async_engine

import bin.config as config

# Weird style formatting?
engine = create_async_engine("postgresql+asyncpg://%s:%s@%s:%s/%s" %
                             (config.get("DB_USER"),
                              config.get("DB_PASS"),
                              config.get("DB_IP"),
                              config.get("DB_PORT"),
                              config.get("DB_NAME"))
                            )

# Add connection pool here