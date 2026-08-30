from __future__ import annotations

from aiobotocore.session import get_session as get_aio_session
from pydantic import BaseModel, Field

from jugo.core.config import get_settings


class PresignRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=1024)
    expires: int = Field(default=3600, ge=60, le=86400)


class PresignResponse(BaseModel):
    url: str
    key: str
    expires: int


async def presign_upload(key: str, expires: int = 3600) -> str:
    settings = get_settings()
    session = get_aio_session()
    async with session.create_client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    ) as client:
        url = await client.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.s3_bucket, "Key": key},
            ExpiresIn=expires,
        )
    return str(url)
