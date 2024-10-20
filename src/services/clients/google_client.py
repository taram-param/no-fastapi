from httpx import AsyncClient

from app.config import settings


class GoogleClient:
    def get_google_oauth_url(self):
        return (
            f"https://accounts.google.com/o/oauth2/auth"
            f"?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            f"&scope=openid%20profile%20email&access_type=offline"
        )

    async def get_google_access_token(self, code: str):
        token_url = "https://accounts.google.com/o/oauth2/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            access_token = response.json().get("access_token")

        return access_token

    async def get_user_info(self, code):
        access_token = await self.get_google_access_token(code)
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            response.raise_for_status()

        return response.json()
