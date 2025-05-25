from fastapi import FastAPI, Depends, HTTPException, WebSocket, UploadFile, File, Request
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, or_, Date, func, Index, case
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
from database.database import Base, Ship, get_db, engine
from database.models import User, ActivityLog
import datetime
import asyncio
import random
import json
import time
from fastapi.background import BackgroundTasks
from fastapi.responses import FileResponse
from Backend.utils.file_operations import save_upload_file, get_file_path, list_files, delete_file
from collections import Counter
from Backend.routers import auth
from Backend.services.monitoring_service import start_monitoring, stop_monitoring, log_activity
from Backend.services.auth_service import get_current_user
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'app.log',
            maxBytes=10000000,
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# =============================================
# FastAPI App Configuration
# =============================================
app = FastAPI(
    title="Naval Ships API",
    description="API for managing a database of naval ships",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") == "production" else "/docs",
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") == "production" else "/redoc"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# CORS settings for both local and production
frontend_origins = [
    "http://localhost:8080",
    os.getenv("FRONTEND_PROD_URL", "https://vue-app-navy-builder-3jddx2ttm-chis-denis-projects.vercel.app")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Create tables for local SQLite development
from database.database import Base, engine
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])

# WebSocket connections store
active_connections: List[WebSocket] = []

# Flag to control automatic ship generation
auto_generation_enabled = True

# Flag to indicate if background task is running
background_task_running = False

# =============================================
# WebSocket Connection Manager
# =============================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global auto_generation_enabled
    await websocket.accept()
    active_connections.append(websocket)
    print(f"WebSocket connection established. Active connections: {len(active_connections)}")
    
    # Default: disable auto-generation when any client connects
    auto_generation_enabled = False
    print("Auto-generation disabled by default on new connection")
    
    try:
        while True:
            message = await websocket.receive_text()
            print(f"Received WebSocket message: {message}")
            
            if message == "disable-auto-generation":
                auto_generation_enabled = False
                await websocket.send_json({"type": "status", "message": "Auto-generation disabled"})
                print("Automatic ship generation disabled via WebSocket message")
            elif message == "generate-ship":
                try:
                    db = next(get_db())
                    new_ships = []
                    
                    # Create all 5 ships at once
                    for _ in range(5):
                        countries = ["USA", "UK", "France", "Germany", "Japan", "Italy"]
                        ship_prefixes = ["USS", "HMS", "FS", "KMS", "IJN", "RN"]
                        ship_types = ["Battleship", "Cruiser", "Destroyer", "Submarine", "Carrier"]
                        
                        country = random.choice(countries)
                        prefix = ship_prefixes[countries.index(country)]
                        ship_name = f"{prefix} {random.choice(ship_types)}-{random.randint(100, 999)}"
                        
                        current_year = datetime.datetime.now().year
                        year_built = random.randint(current_year - 50, current_year)
                        commissioned = year_built + random.randint(0, 2)
                        stricken = commissioned + random.randint(5, 30)
                        
                        new_ship = Ship(
                            name=ship_name,
                            year_built=year_built,
                            commissioned_date=commissioned,
                            stricken_date=stricken,
                            country_of_origin=country
                        )
                        
                        db.add(new_ship)
                        new_ships.append(new_ship)
                    
                    # Commit all ships at once
                    db.commit()
                    
                    # Refresh all ships to get their IDs
                    for ship in new_ships:
                        db.refresh(ship)
                    
                    # Send all ships in quick succession
                    for ship in new_ships:
                        ship_data = {
                            "id": ship.id,
                            "name": ship.name,
                            "year_built": ship.year_built,
                            "commissioned_date": ship.commissioned_date,
                            "stricken_date": ship.stricken_date,
                            "country_of_origin": ship.country_of_origin,
                            "source": "system"
                        }
                        
                        await notify_clients({
                            "type": "new_ship",
                            "data": ship_data
                        })
                    
                except Exception as e:
                    print(f"Error generating ships: {str(e)}")
                finally:
                    db.close()
    except:
        active_connections.remove(websocket)

async def notify_clients(data: dict):
    """Send updates to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except:
            active_connections.remove(connection)

# =============================================
# Background Task for Ship Generation
# =============================================
async def generate_ships_background():
    """Background task to generate new ships periodically"""
    global auto_generation_enabled, background_task_running
    
    # Set flag to indicate task is running
    background_task_running = True
    print("Background ship generation task started")
    
    while background_task_running:
        # Skip ship generation if auto generation is disabled
        if not auto_generation_enabled:
            print("Auto-generation is disabled, skipping ship generation cycle")
            await asyncio.sleep(5)
            continue
            
        try:
            db = next(get_db())
            
            # Generate a random ship
            countries = ["USA", "UK", "France", "Germany", "Japan", "Italy"]
            ship_prefixes = ["USS", "HMS", "FS", "KMS", "IJN", "RN"]
            ship_types = ["Battleship", "Cruiser", "Destroyer", "Submarine", "Carrier"]
            
            country = random.choice(countries)
            prefix = ship_prefixes[countries.index(country)]
            ship_name = f"{prefix} {random.choice(ship_types)}-{random.randint(100, 999)}"
            
            current_year = datetime.datetime.now().year
            year_built = random.randint(current_year - 50, current_year)
            commissioned = year_built + random.randint(0, 2)
            stricken = commissioned + random.randint(5, 30)
            
            new_ship = Ship(
                name=ship_name,
                year_built=year_built,
                commissioned_date=commissioned,
                stricken_date=stricken,
                country_of_origin=country
            )
            
            db.add(new_ship)
            db.commit()
            db.refresh(new_ship)
            
            # Notify all connected clients
            ship_data = {
                "id": new_ship.id,
                "name": new_ship.name,
                "year_built": new_ship.year_built,
                "commissioned_date": new_ship.commissioned_date,
                "stricken_date": new_ship.stricken_date,
                "country_of_origin": new_ship.country_of_origin,
                "source": "system"  # Add source information for system-generated ships
            }
            
            await notify_clients({
                "type": "new_ship",
                "data": ship_data
            })
            
        except Exception as e:
            print(f"Error in ship generation: {str(e)}")
        finally:
            db.close()
        
        # Wait for 10 seconds before generating the next ship
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    global background_task_running
    background_task_running = True
    asyncio.create_task(generate_ships_background())
    start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on application shutdown"""
    global background_task_running
    background_task_running = False
    stop_monitoring()

# =============================================
# Pydantic Models (API Schema)
# =============================================
class ShipBase(BaseModel):
    """Base Pydantic model for ship data"""
    name: str
    year_built: int
    commissioned_date: Optional[int] = None
    stricken_date: Optional[int] = None
    country_of_origin: Optional[str] = None

class ShipCreate(ShipBase):
    """Pydantic model for creating ships"""
    pass

class ShipResponse(ShipBase):
    """Pydantic model for ship responses"""
    id: int
    class Config:
        from_attributes = True

# =============================================
# API Routes
# =============================================
@app.get("/ships/", response_model=List[ShipResponse])
async def get_ships(
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ships = db.query(Ship).all()
    log_activity(
        db=db,
        user_id=current_user.id,
        action="READ",
        entity_type="ships",
        entity_id=None,
        details="Retrieved all ships"
    )
    return ships

@app.post("/ships/", response_model=ShipResponse)
async def add_ship(
    ship: ShipCreate,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ship = Ship(**ship.dict())
    db.add(db_ship)
    db.commit()
    db.refresh(db_ship)
    
    log_activity(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="ship",
        entity_id=db_ship.id,
        details=f"Created new ship: {db_ship.name}"
    )
    
    return db_ship

@app.get("/ships/search/", response_model=List[ShipResponse])
async def search_ships(query: str, db = Depends(get_db)):
    """Search ships by name, year, dates, or country"""
    search = f"%{query}%"
    return db.query(Ship).filter(
        or_(
            Ship.name.ilike(search),
            Ship.country_of_origin.ilike(search),
            Ship.year_built.cast(String).ilike(search),
            Ship.commissioned_date.cast(String).ilike(search),
            Ship.stricken_date.cast(String).ilike(search)
        )
    ).all()

@app.get("/ships/filter/", response_model=List[ShipResponse])
async def filter_ships(
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    commissioned_from: Optional[int] = None,
    commissioned_to: Optional[int] = None,
    country: Optional[str] = None,
    db = Depends(get_db)
):
    """Filter ships by year range and country"""
    query = db.query(Ship)
    
    if year_from is not None:
        query = query.filter(Ship.year_built >= year_from)
    if year_to is not None:
        query = query.filter(Ship.year_built <= year_to)
    if commissioned_from is not None:
        query = query.filter(Ship.commissioned_date >= commissioned_from)
    if commissioned_to is not None:
        query = query.filter(Ship.commissioned_date <= commissioned_to)
    if country:
        query = query.filter(Ship.country_of_origin.ilike(f"%{country}%"))
    
    return query.all()

@app.put("/ships/{ship_id}", response_model=ShipResponse)
async def update_ship(
    ship_id: int,
    ship: ShipCreate,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not db_ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    for key, value in ship.dict().items():
        setattr(db_ship, key, value)
    
    db.commit()
    db.refresh(db_ship)
    
    log_activity(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="ship",
        entity_id=ship_id,
        details=f"Updated ship: {db_ship.name}"
    )
    
    return db_ship

@app.delete("/ships/{ship_id}")
async def delete_ship(
    ship_id: int,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not db_ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    ship_name = db_ship.name
    db.delete(db_ship)
    db.commit()
    
    log_activity(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="ship",
        entity_id=ship_id,
        details=f"Deleted ship: {ship_name}"
    )
    
    return {"message": "Ship deleted successfully"}

@app.get("/ships/sort/", response_model=List[ShipResponse])
async def sort_ships(
    field: str = "year_built",
    ascending: bool = True,
    db = Depends(get_db)
):
    """Sort ships by specified field and direction"""
    valid_fields = {
        "year_built": Ship.year_built,
        "commissioned_date": Ship.commissioned_date,
        "stricken_date": Ship.stricken_date,
        "name": Ship.name,
        "country_of_origin": Ship.country_of_origin
    }

    if field not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Valid fields are: {', '.join(valid_fields.keys())}")

    sort_field = valid_fields[field]
    query = db.query(Ship)

    if ascending:
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())

    return query.all()

@app.get("/ships/sort/service-duration/", response_model=List[ShipResponse])
async def sort_by_service_duration(
    ascending: bool = True,
    db = Depends(get_db)
):
    """Sort ships by their service duration (stricken_date - commissioned_date)"""
    query = db.query(Ship)
    
    # Filter out ships without both dates
    query = query.filter(
        Ship.commissioned_date.isnot(None),
        Ship.stricken_date.isnot(None)
    )
    
    # Calculate service duration using SQLAlchemy expression
    service_duration = Ship.stricken_date - Ship.commissioned_date
    
    if ascending:
        query = query.order_by(service_duration.asc())
    else:
        query = query.order_by(service_duration.desc())
    
    return query.all()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/auto-generation/status")
async def auto_generation_status():
    """Check if automatic ship generation is enabled"""
    return {"enabled": auto_generation_enabled}

@app.post("/auto-generation/toggle")
async def toggle_auto_generation(enable: bool = False):
    """Enable or disable automatic ship generation"""
    global auto_generation_enabled
    auto_generation_enabled = enable
    print(f"Auto-generation set to: {enable}")
    
    # Ensure we notify all connected clients
    try:
        await notify_clients({
            "type": "auto_generation",
            "enabled": enable
        })
    except Exception as e:
        print(f"Error notifying clients: {e}")
    
    return {"enabled": auto_generation_enabled}

@app.post("/auto-generation/stop")
async def stop_background_task():
    """Stop the background ship generation task completely"""
    global background_task_running
    background_task_running = False
    print("Background task stopping signal sent")
    return {"status": "stopping"}

# =============================================
# File Operations Routes
# =============================================
@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the server"""
    return await save_upload_file(file)

@app.get("/files/download/{filename}")
async def download_file(filename: str):
    """Download a file from the server"""
    file_path = get_file_path(filename)
    return FileResponse(file_path, filename=filename)

@app.get("/files/list", response_model=List[str])
async def get_files():
    """List all available files"""
    return list_files()

@app.delete("/files/{filename}")
async def remove_file(filename: str):
    """Delete a file from the server"""
    return delete_file(filename)

@app.get("/ships/statistics")
async def get_ship_statistics(db = Depends(get_db)):
    """Get ship statistics using optimized database queries"""
    # Get total count
    total = db.query(func.count(Ship.id)).scalar()
    
    if total == 0:
        return {
            "total": 0,
            "most_common_country": None,
            "most_common_country_count": 0,
            "active": 0,
            "retired": 0,
            "oldest_year": None,
            "newest_year": None
        }
    
    # Get most common country using SQL aggregation
    most_common = db.query(
        Ship.country_of_origin,
        func.count(Ship.id).label('count')
    ).filter(
        Ship.country_of_origin.isnot(None)
    ).group_by(
        Ship.country_of_origin
    ).order_by(
        func.count(Ship.id).desc()
    ).first()
    
    most_common_country = most_common[0] if most_common else None
    most_common_country_count = most_common[1] if most_common else 0
    
    # Get active/retired counts using SQL aggregation
    status_counts = db.query(
        func.sum(case((Ship.stricken_date.is_(None), 1), else_=0)).label('active'),
        func.sum(case((Ship.stricken_date.isnot(None), 1), else_=0)).label('retired')
    ).first()
    
    active = status_counts[0] or 0
    retired = status_counts[1] or 0
    
    # Get oldest/newest year using SQL aggregation
    year_stats = db.query(
        func.min(Ship.year_built).label('oldest'),
        func.max(Ship.year_built).label('newest')
    ).first()
    
    oldest_year = year_stats[0]
    newest_year = year_stats[1]
    
    return {
        "total": total,
        "most_common_country": most_common_country,
        "most_common_country_count": most_common_country_count,
        "active": active,
        "retired": retired,
        "oldest_year": oldest_year,
        "newest_year": newest_year
    }

async def get_ship_statistics_old(db = Depends(get_db)):
    """Original implementation of ship statistics"""
    start_time = time.time()
    
    ships = db.query(Ship).all()
    total = len(ships)
    if not ships:
        return {
            "total": 0,
            "most_common_country": None,
            "most_common_country_count": 0,
            "active": 0,
            "retired": 0,
            "oldest_year": None,
            "newest_year": None
        }
    
    # Most common country
    countries = [ship.country_of_origin for ship in ships if ship.country_of_origin]
    if countries:
        country_counter = Counter(countries)
        most_common_country, most_common_country_count = country_counter.most_common(1)[0]
    else:
        most_common_country, most_common_country_count = None, 0
    
    # Active/retired
    active = sum(1 for ship in ships if not ship.stricken_date)
    retired = sum(1 for ship in ships if ship.stricken_date)
    
    # Oldest/newest year
    years = [ship.year_built for ship in ships if ship.year_built]
    oldest_year = min(years) if years else None
    newest_year = max(years) if years else None
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return {
        "total": total,
        "most_common_country": most_common_country,
        "most_common_country_count": most_common_country_count,
        "active": active,
        "retired": retired,
        "oldest_year": oldest_year,
        "newest_year": newest_year,
        "execution_time": execution_time
    }

@app.get("/ships/statistics/benchmark")
async def benchmark_statistics(db = Depends(get_db)):
    """Compare performance between old and new implementations"""
    # Run old implementation
    old_start = time.time()
    old_result = await get_ship_statistics_old(db)
    old_time = old_result["execution_time"]
    
    # Run new implementation
    new_start = time.time()
    new_result = await get_ship_statistics(db)
    new_time = time.time() - new_start
    
    # Calculate improvement percentage
    improvement = ((old_time - new_time) / old_time) * 100
    
    return {
        "old_implementation_time": old_time,
        "new_implementation_time": new_time,
        "improvement_percentage": improvement,
        "old_result": {k: v for k, v in old_result.items() if k != "execution_time"},
        "new_result": new_result
    }

@app.get("/ships/page/")
async def get_ships_page(page: int = 1, page_size: int = 10, db=Depends(get_db)):
    query = db.query(Ship).order_by(Ship.id)
    # Only count if the dataset is not huge
    total = None
    count_threshold = 1000
    try:
        total = query.count()
    except Exception:
        total = None
    ships = query.offset((page - 1) * page_size).limit(page_size).all()
    # If total is above threshold, don't return it
    if total is not None and total > count_threshold:
        total = None
    return {
        "ships": [ShipResponse.model_validate(ship) for ship in ships],
        "total": total
    }

#cd C:\Chestii\Programe\Sqlite
#sqlite3 C:\Chestii\Programe\Sqlite\TabelMPP\navy.db
#npm run serve
#uvicorn main:app --reload