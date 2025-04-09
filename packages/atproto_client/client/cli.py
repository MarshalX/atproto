import os
import asyncio
import aiohttp
from typing import Callable, Any
from authlib.jose import JsonWebKey

from atproto_client import AsyncClient, Session, SessionEvent
from atproto_client.exceptions import UnauthorizedError


async def fetch_credentials(aip_jwk: str, aip_server: str = "https://grazeaip.tunn.dev") -> Session:
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {aip_jwk}",
        }
        async with session.get(f"{aip_server}/internal/api/me", headers=headers) as response:
            me_response = await response.json()

            if "error" in me_response:
                raise Exception(me_response["error"])

            oauth_session_valid = me_response.get("oauth_session_valid", False)
            app_password_session_valid = me_response.get(
                "app_password_session_valid", False)

            if not oauth_session_valid and not app_password_session_valid:
                raise Exception("No valid session found")

        async with session.get(f"{aip_server}/internal/api/credentials", headers=headers) as response:
            session_response = await response.json()

            if "error" in session_response:
                raise Exception(session_response["error"])

            if "type" in session_response and session_response["type"] == "dpop":
                session = Session(
                    handle=me_response.get("handle", ""),
                    did=me_response.get("did", ""),
                    pds_endpoint=me_response.get("pds", None),
                    static_dpop_token=session_response.get("token", None),
                    static_dpop_issuer=session_response.get("issuer", None),
                    static_dpop_jwk=JsonWebKey.import_key(session_response.get("jwk", None)),
                )
                return session
    raise Exception("oops")


async def retry_invoke(client: AsyncClient, session: Session, func: Callable, *args, **kwargs) -> Any:
    for i in range(2):
        try:
            return await func(*args, **kwargs)
        except UnauthorizedError as e:
            if e.response is not None and e.response.status_code == 401:
                if "www-authenticate" in e.response.headers and "use_dpop_nonce" in e.response.headers["www-authenticate"]:
                    session.static_dpop_nonce = e.response.headers["dpop-nonce"]
                    continue
            raise e

async def realMain() -> None:
    session = await fetch_credentials(os.getenv("AIP_JWK", ""), "https://auth.m.graze.social")

    client = AsyncClient()
    await client._set_session(SessionEvent.IMPORT, session)

    create_record_args = {
        "collection": "garden.lexicon.deeply-mouse.profile",
        "repo": session.did,
        "record": {
            "$type": "garden.lexicon.deeply-mouse.profile",
            "name": session.handle,
        },
        "validate": False,
    }


    created_record = await retry_invoke(client, session, client.com.atproto.repo.create_record, {**create_record_args})
    print(created_record)

    records = await retry_invoke(client, session, client.com.atproto.repo.list_records, {"collection": "garden.lexicon.deeply-mouse.profile", "repo": session.did})
    print(records)


def main() -> None:
    asyncio.run(realMain())


if __name__ == '__main__':
    main()
