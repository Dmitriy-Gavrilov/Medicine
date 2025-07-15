from httpx import AsyncClient

from app.exceptions.routing import RoutingException
from app.schemas.team import CoordinatesSchema

from app.settings import settings


class Router:
    def __init__(self):
        self.api_url = settings.ROUTE_API_URL

    async def get_route(self,
                        team_coordinates: CoordinatesSchema,
                        call_coordinates: CoordinatesSchema
                        ) -> list[CoordinatesSchema]:

        url = (f"{self.api_url}/"
               f"{team_coordinates.lon},{team_coordinates.lat};"
               f"{call_coordinates.lon},{call_coordinates.lat}"
               f"?overview=full&steps=true&geometries=geojson")

        try:
            async with AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                route = response.json()["routes"][0]["geometry"]["coordinates"]
                res = [CoordinatesSchema(lon=route[i][0], lat=route[i][1]) for i in range(0, len(route), 3)]
                return res
        except Exception:
            raise RoutingException()
