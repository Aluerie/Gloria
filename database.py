from __future__ import annotations

from typing import Any

import asyncpg
import orjson

import config


async def create_pool() -> asyncpg.Pool[asyncpg.Record]:
    """Create a database connection pool."""

    def _encode_jsonb(value: Any) -> str:
        return orjson.dumps(value).decode("utf-8")

    def _decode_jsonb(value: str) -> Any:
        return orjson.loads(value)

    async def init(con: asyncpg.Connection[asyncpg.Record]) -> None:
        await con.set_type_codec(
            "jsonb",
            schema="pg_catalog",
            encoder=_encode_jsonb,
            decoder=_decode_jsonb,
            format="text",
        )

    return await asyncpg.create_pool(
        config.POSTGRES_URL,
        init=init,
        command_timeout=60,
        min_size=20,
        max_size=20,
        # record_class=DotRecord,  # deprecated
        statement_cache_size=0,
    )  # pyright: ignore[reportReturnType]
