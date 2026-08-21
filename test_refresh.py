import asyncio

from supabase import create_client

from config.settings import get_settings


async def main():
    settings = get_settings()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    print(dir(client.auth))
    # We can't really test refresh_session without a valid refresh_token, but we can check if it exists and what arguments it takes.
    import inspect

    print(inspect.signature(client.auth.refresh_session))


if __name__ == "__main__":
    asyncio.run(main())
