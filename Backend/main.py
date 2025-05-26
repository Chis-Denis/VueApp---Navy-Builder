from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, or_, Date, func, Index, case
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
from database.database import Base, Ship, get_db, engine
from database.models import User, ActivityLog
import datetime
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
from starlette.datastructures import CommaSeparatedStrings
from ast import literal_eval

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
    "https://vue-app-navy-builder-88la3cfn3-chis-denis-projects.vercel.app",  # your Vercel frontend
    "http://localhost:8080"  # for local testing
]

cors_env = os.getenv("CORS_ORIGINS", "[]")
cors_origins = literal_eval(cors_env)  # Parses stringified list

# Ensure the main frontend is always included
if "https://vue-app-navy-builder-88la3cfn3-chis-denis-projects.vercel.app" not in cors_origins:
    cors_origins.append("https://vue-app-navy-builder-88la3cfn3-chis-denis-projects.vercel.app")
if "http://localhost:8080" not in cors_origins:
    cors_origins.append("http://localhost:8080")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],
)

print("Loaded CORS origins:", cors_origins)

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

@app.on_event("startup")
async def startup_event():
    """Start monitoring on application startup"""
    start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop monitoring on application shutdown"""
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