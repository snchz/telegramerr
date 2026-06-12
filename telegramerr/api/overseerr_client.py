import aiohttp
from typing import Optional, Dict, Any, List, Union
import urllib.parse
import logging
from telegramerr.config import settings

class OverseerrClient:
    def __init__(self):
        self.base_url = settings.OVERSEERR_URL.rstrip('/')
        self.api_key = settings.OVERSEERR_API_KEY
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def search(self, query: str, page: int = 1) -> Dict[str, Any]:
        logging.debug(f"[Overseerr] Iniciando búsqueda: query='{query}', page={page}")
        async with aiohttp.ClientSession() as session:
            safe_query = urllib.parse.quote(query)
            url = f"{self.base_url}/api/v1/search?query={safe_query}&page={page}"
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    err_text = await response.text()
                    logging.error(f"[Overseerr] Error en búsqueda HTTP {response.status}: {err_text}")
                    raise Exception(f"{response.status} - {err_text}")
                data = await response.json()
                logging.debug(f"[Overseerr] Búsqueda devuelta exitosamente con {len(data.get('results', []))} resultados.")
                return data

    async def get_trending(self, page: int = 1) -> Dict[str, Any]:
        logging.debug(f"[Overseerr] Obteniendo tendencias, página {page}")
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v1/discover/trending?page={page}"
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    err_text = await response.text()
                    logging.error(f"[Overseerr] Error obteniendo tendencias HTTP {response.status}: {err_text}")
                    raise Exception(f"{response.status} - {err_text}")
                return await response.json()
                
    async def get_tv_details(self, tmdb_id: int) -> Dict[str, Any]:
        logging.debug(f"[Overseerr] Obteniendo detalles de TV para TMDB ID: {tmdb_id}")
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v1/tv/{tmdb_id}"
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    err_text = await response.text()
                    logging.error(f"[Overseerr] Error obteniendo detalles TV HTTP {response.status}: {err_text}")
                    raise Exception(f"{response.status} - {err_text}")
                return await response.json()

    async def get_media_title(self, media_type: str, tmdb_id: int) -> str:
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v1/{media_type}/{tmdb_id}"
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("title") or data.get("name") or "Media"
                return "Media"

    async def request_media(self, media_type: str, media_id: int, seasons: Optional[List[int]], overseerr_user_id: int) -> bool:
        logging.info(f"[Overseerr] Solicitando {media_type} ID {media_id} para usuario Overseerr {overseerr_user_id} (Temporadas: {seasons})")
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v1/request"
            payload: Dict[str, Any] = {
                "mediaType": media_type,
                "mediaId": media_id,
            }
            if media_type == "tv" and seasons:
                payload["seasons"] = seasons
            elif media_type == "tv":
                payload["seasons"] = "all"
                
            logging.debug(f"[Overseerr] Payload de petición: {payload}")
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status in (200, 201):
                    logging.info(f"[Overseerr] Petición creada con éxito para {media_type} ID {media_id}.")
                    return True
                else:
                    try:
                        err = await response.json()
                        logging.error(f"[Overseerr] Error al crear petición HTTP {response.status}: {err}")
                    except Exception as e:
                        logging.error(f"[Overseerr] Error desconocido al crear petición HTTP {response.status}: {e}")
                    return False
                    
    async def get_requests(self) -> Dict[str, Any]:
        logging.debug(f"[Overseerr] Haciendo polling de peticiones actuales...")
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v1/request"
            params = {"take": 50, "sort": "added"}
            async with session.get(url, headers=self.headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                logging.debug(f"[Overseerr] Polling recuperó {len(data.get('results', []))} peticiones recientes.")
                return data

overseerr = OverseerrClient()
