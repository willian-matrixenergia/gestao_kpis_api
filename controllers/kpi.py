from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from schemas.kpi import KpiResponse, KpiCreate, KpiUpdate
from services.kpi import kpi_service

router = APIRouter(
    prefix="/kpis", 
    tags=["kpis"]
)

@router.post("/", response_model=KpiResponse)
def create_kpi(kpi: KpiCreate, db: Session = Depends(get_db)):
    db_kpi = kpi_service.get_kpi(db, id_kpi=kpi.id_kpi)
    if db_kpi:
        raise HTTPException(status_code=400, detail="KPI id already registered")
    return kpi_service.create_kpi(db=db, kpi=kpi)

@router.get("/", response_model=List[KpiResponse])
def read_kpis(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    kpis = kpi_service.get_kpis(db, skip=skip, limit=limit)
    return kpis

@router.get("/{id_kpi}", response_model=KpiResponse)
def read_kpi(id_kpi: str, db: Session = Depends(get_db)):
    db_kpi = kpi_service.get_kpi(db, id_kpi=id_kpi)
    if db_kpi is None:
        raise HTTPException(status_code=404, detail="KPI not found")
    return db_kpi

@router.put("/{id_kpi}", response_model=KpiResponse)
def update_kpi(id_kpi: str, kpi: KpiUpdate, db: Session = Depends(get_db)):
    db_kpi = kpi_service.update_kpi(db, id_kpi=id_kpi, kpi=kpi)
    if db_kpi is None:
        raise HTTPException(status_code=404, detail="KPI not found")
    return db_kpi

@router.delete("/{id_kpi}", response_model=KpiResponse)
def delete_kpi(id_kpi: str, db: Session = Depends(get_db)):
    db_kpi = kpi_service.delete_kpi(db, id_kpi=id_kpi)
    if db_kpi is None:
        raise HTTPException(status_code=404, detail="KPI not found")
    return db_kpi
