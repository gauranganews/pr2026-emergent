from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import httpx
import base64
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Astrology API Configuration
ASTROLOGY_USER_ID = os.environ.get('ASTROLOGY_USER_ID')
ASTROLOGY_API_KEY = os.environ.get('ASTROLOGY_API_KEY')
ASTROLOGY_BASE_URL = "https://json.astrologyapi.com/v1"

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Models
class BirthData(BaseModel):
    day: int
    month: int
    year: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    timezone: float

class CitySearchRequest(BaseModel):
    query: str

class CityResult(BaseModel):
    name: str
    latitude: float
    longitude: float
    timezone: float
    country: str

class AstroRequest(BaseModel):
    birthDate: str  # YYYY-MM-DD
    birthTime: str  # HH:MM
    latitude: float
    longitude: float
    timezone: float

class PlanetPosition(BaseModel):
    name: str
    sign: str
    degree: str
    house: Optional[int] = None

class VdashaDetails(BaseModel):
    planet: str
    start: str
    end: str

class AstroResponse(BaseModel):
    planets: List[Dict[str, Any]]
    vdasha: List[Dict[str, Any]]
    prediction: str


# Helper function to call Astrology API
async def call_astrology_api(endpoint: str, data: dict) -> dict:
    """Call Astrology API with authentication"""
    auth_string = f"{ASTROLOGY_USER_ID}:{ASTROLOGY_API_KEY}"
    auth_bytes = auth_string.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_auth = base64_bytes.decode('ascii')
    
    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Content-Type": "application/json"
    }
    
    url = f"{ASTROLOGY_BASE_URL}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logging.error(f"Astrology API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Astrology API error: {str(e)}")


# Routes
@api_router.get("/")
async def root():
    return {"message": "Astro Prediction API"}


@api_router.post("/search-city", response_model=List[CityResult])
async def search_city(request: CitySearchRequest):
    """Search for cities using Nominatim (OpenStreetMap)"""
    query = request.query
    
    if not query or len(query) < 2:
        return []
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 5,
        "addressdetails": 1
    }
    
    headers = {
        "User-Agent": "AstroApp/1.0"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            results = response.json()
            
            cities = []
            for result in results:
                # Get timezone using timezonefinder logic or default
                # For simplicity, we'll estimate timezone based on longitude
                # Real implementation should use a timezone API
                timezone_offset = round(float(result['lon']) / 15)
                
                city_name = result.get('display_name', result.get('name', 'Unknown'))
                country = result.get('address', {}).get('country', '')
                
                cities.append(CityResult(
                    name=city_name,
                    latitude=float(result['lat']),
                    longitude=float(result['lon']),
                    timezone=timezone_offset,
                    country=country
                ))
            
            return cities
        except Exception as e:
            logging.error(f"City search error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"City search error: {str(e)}")


@api_router.post("/get-prediction", response_model=AstroResponse)
async def get_prediction(request: AstroRequest):
    """Get astrological prediction for 2026"""
    try:
        # Validate and parse date and time
        try:
            date_parts = request.birthDate.split('-')
            time_parts = request.birthTime.split(':')
            
            if len(date_parts) != 3 or len(time_parts) != 2:
                raise HTTPException(
                    status_code=422,
                    detail="Неверный формат даты или времени. Используйте YYYY-MM-DD и HH:MM"
                )
            
            birth_data = {
                "day": int(date_parts[2]),
                "month": int(date_parts[1]),
                "year": int(date_parts[0]),
                "hour": int(time_parts[0]),
                "min": int(time_parts[1]),
                "lat": request.latitude,
                "lon": request.longitude,
                "tzone": request.timezone
            }
            
            # Basic validation
            if not (1 <= birth_data["day"] <= 31):
                raise HTTPException(status_code=422, detail="День должен быть от 1 до 31")
            if not (1 <= birth_data["month"] <= 12):
                raise HTTPException(status_code=422, detail="Месяц должен быть от 1 до 12")
            if not (1900 <= birth_data["year"] <= 2100):
                raise HTTPException(status_code=422, detail="Год должен быть от 1900 до 2100")
            if not (0 <= birth_data["hour"] <= 23):
                raise HTTPException(status_code=422, detail="Час должен быть от 0 до 23")
            if not (0 <= birth_data["min"] <= 59):
                raise HTTPException(status_code=422, detail="Минуты должны быть от 0 до 59")
                
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Неверный формат данных. Проверьте правильность введённых значений"
            )
        
        # Get planets data
        planets_response = await call_astrology_api("planets", birth_data)
        
        # Get birth details (for Rashi, etc.)
        birth_details_response = await call_astrology_api("birth_details", birth_data)
        
        # Get Vdasha (major periods)
        vdasha_response = await call_astrology_api("major_vdasha", birth_data)
        
        # Process planets data
        planets_list = []
        if isinstance(planets_response, list):
            for planet in planets_response:
                planets_list.append({
                    "name": planet.get('name', ''),
                    "sign": planet.get('sign', ''),
                    "degree": planet.get('normDegree', ''),
                    "nakshatra": planet.get('nakshatra', ''),
                    "house": planet.get('house', '')
                })
        
        # Process Vdasha data - filter for 2026
        vdasha_list = []
        # API returns a list directly, not a dict with 'major_vdasha' key
        if isinstance(vdasha_response, list):
            # Log all periods for debugging
            logging.info(f"Total vdasha periods: {len(vdasha_response)}")
            if vdasha_response:
                logging.info(f"First period: {vdasha_response[0]}")
                logging.info(f"Last period: {vdasha_response[-1]}")
            
            for vdasha in vdasha_response:
                # Check if this vdasha includes 2026
                start_date = vdasha.get('start', '')
                end_date = vdasha.get('end', '')
                
                # Parse dates - format is DD-MM-YYYY
                if start_date and end_date:
                    try:
                        # Split date format DD-MM-YYYY
                        start_parts = start_date.split('-')
                        end_parts = end_date.split('-')
                        
                        if len(start_parts) == 3 and len(end_parts) == 3:
                            start_year = int(start_parts[2])
                            end_year = int(end_parts[2])
                            
                            # Check if 2026 falls within the period
                            if start_year <= 2026 <= end_year:
                                logging.info(f"Found matching period: {vdasha.get('planet')} from {start_date} to {end_date}")
                                vdasha_list.append({
                                    "planet": vdasha.get('planet', ''),
                                    "start": start_date,
                                    "end": end_date
                                })
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Failed to parse vdasha dates: {start_date} - {end_date}: {str(e)}")
        elif isinstance(vdasha_response, dict) and 'major_vdasha' in vdasha_response:
            # Fallback in case API structure changes
            for vdasha in vdasha_response['major_vdasha']:
                start_date = vdasha.get('start', '')
                end_date = vdasha.get('end', '')
                
                if start_date and end_date:
                    try:
                        start_parts = start_date.split('-')
                        end_parts = end_date.split('-')
                        
                        if len(start_parts) == 3 and len(end_parts) == 3:
                            start_year = int(start_parts[2])
                            end_year = int(end_parts[2])
                            
                            if start_year <= 2026 <= end_year:
                                vdasha_list.append({
                                    "planet": vdasha.get('planet', ''),
                                    "start": start_date,
                                    "end": end_date
                                })
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Failed to parse vdasha dates: {start_date} - {end_date}: {str(e)}")
        
        # Prepare data for GPT
        astro_data_text = f"""Астрологические данные:
        
Положение планет:
{chr(10).join([f"- {p['name']}: {p['sign']}, {p['degree']}°, Накшатра: {p['nakshatra']}" for p in planets_list])}

Периоды (Махадаша) на 2026 год:
{chr(10).join([f"- {v['planet']}: с {v['start']} по {v['end']}" for v in vdasha_list])}
"""
        
        # Generate prediction using GPT-5.1
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"astro_{datetime.now(timezone.utc).timestamp()}",
            system_message="Ты опытный астролог. Отвечай на русском языке."
        ).with_model("openai", "gpt-5.1")
        
        prompt = f"{astro_data_text}\n\nСоставь краткий астрологический прогноз на 2026 год для человека в один абзац. Объясни основные тенденции года и смены периодов. Чего ожидать и к чему готовиться."
        
        user_message = UserMessage(text=prompt)
        prediction = await chat.send_message(user_message)
        
        return AstroResponse(
            planets=planets_list,
            vdasha=vdasha_list,
            prediction=prediction
        )
        
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()