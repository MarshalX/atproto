import os
import asyncio
import aiohttp
from authlib.jose import JsonWebKey

from atproto_client import AsyncClient, Session, SessionEvent


async def fetch_credentials(aip_jwk: str, aip_server: str = "https://auth.m.graze.social") -> dict:
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
                    static_dpop_nonce="Uuc5_cgxd_V8iEK4pq3u90zMeb8AdP-7E61049HTu-4",
                )
                return session
    raise Exception("oops")


async def realMain() -> None:
    session = await fetch_credentials(os.getenv("AIP_JWK"))

    client = AsyncClient()
    await client._set_session(SessionEvent.IMPORT, session)
    timeline = await client.get_timeline()

    print(timeline)


def main() -> None:
    asyncio.run(realMain())


if __name__ == '__main__':
    main()
