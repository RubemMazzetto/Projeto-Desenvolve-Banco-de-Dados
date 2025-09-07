from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, Column, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from pydantic import BaseModel, constr
from typing import Dict, Any
import geojson
from uuid import uuid4

# Configuração do banco de dados MySQL com PostGIS
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/ze_delivery"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo SQLAlchemy para Partner
class Partner(Base):
    __tablename__ = "partners"
    id = Column(String(36), primary_key=True, index=True)
    tradingName = Column(String(255), nullable=False)
    ownerName = Column(String(255), nullable=False)
    document = Column(String(50), unique=True, nullable=False)
    coverageArea = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    address = Column(Geometry("POINT", srid=4326), nullable=False)
    __table_args__ = (UniqueConstraint("id", "document"),)

# Modelo Pydantic para validação
class PartnerCreate(BaseModel):
    tradingName: constr(min_length=1)
    ownerName: constr(min_length=1)
    document: constr(min_length=1)
    coverageArea: Dict[str, Any]  # GeoJSON MultiPolygon
    address: Dict[str, Any]  # GeoJSON Point

class PartnerResponse(PartnerCreate):
    id: str

# Inicialização do FastAPI
app = FastAPI(title="Zé Delivery Backend Challenge")

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

@app.post("/partners", response_model=PartnerResponse)
async def create_partner(partner: PartnerCreate):
    # Validar GeoJSON
    try:
        coverage_area = geojson.loads(geojson.dumps(partner.coverageArea))
        address = geojson.loads(geojson.dumps(partner.address))
        if not isinstance(coverage_area, geojson.MultiPolygon):
            raise ValueError("coverageArea must be a MultiPolygon")
        if not isinstance(address, geojson.Point):
            raise ValueError("address must be a Point")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db = SessionLocal()
    try:
        # Verificar unicidade
        if db.query(Partner).filter(Partner.document == partner.document).first():
            raise HTTPException(status_code=400, detail="Document already exists")

        partner_id = str(uuid4())
        db_partner = Partner(
            id=partner_id,
            tradingName=partner.tradingName,
            ownerName=partner.ownerName,
            document=partner.document,
            coverageArea=geojson.dumps(partner.coverageArea),
            address=geojson.dumps(partner.address)
        )
        db.add(db_partner)
        db.commit()
        db.refresh(db_partner)
        return PartnerResponse(
            id=partner_id,
            tradingName=partner.tradingName,
            ownerName=partner.ownerName,
            document=partner.document,
            coverageArea=partner.coverageArea,
            address=partner.address
        )
    finally:
        db.close()

@app.get("/partners/{id}", response_model=PartnerResponse)
async def get_partner(id: str):
    db = SessionLocal()
    try:
        partner = db.query(Partner).filter(Partner.id == id).first()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        return PartnerResponse(
            id=partner.id,
            tradingName=partner.tradingName,
            ownerName=partner.ownerName,
            document=partner.document,
            coverageArea=geojson.loads(partner.coverageArea),
            address=geojson.loads(partner.address)
        )
    finally:
        db.close()

@app.get("/partners/search", response_model=PartnerResponse)
async def search_partner(lat: float = Query(...), long: float = Query(...)):
    db = SessionLocal()
    try:
        # Buscar parceiro cuja coverageArea contém o ponto e ordenar por distância
        point = f"POINT({long} {lat})"
        query = db.query(Partner).filter(
            Partner.coverageArea.ST_Contains(point)
        ).order_by(
            Partner.address.ST_Distance(point)
        )
        partner = query.first()
        if not partner:
            raise HTTPException(status_code=404, detail="No partner found in coverage area")
        return PartnerResponse(
            id=partner.id,
            tradingName=partner.tradingName,
            ownerName=partner.ownerName,
            document=partner.document,
            coverageArea=geojson.loads(partner.coverageArea),
            address=geojson.loads(partner.address)
        )
    finally:
        db.close()