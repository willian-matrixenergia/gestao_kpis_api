from sqlalchemy.orm import Session
from models.kpi import Kpi
from schemas.kpi import KpiCreate, KpiUpdate

class KpiService:
    def get_kpi(self, db: Session, id_kpi: str):
        return db.query(Kpi).filter(Kpi.id_kpi == id_kpi).first()

    def get_kpis(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Kpi).offset(skip).limit(limit).all()

    def create_kpi(self, db: Session, kpi: KpiCreate):
        db_kpi = Kpi(**kpi.model_dump())
        db.add(db_kpi)
        db.commit()
        db.refresh(db_kpi)
        return db_kpi

    def update_kpi(self, db: Session, id_kpi: str, kpi: KpiUpdate):
        db_kpi = self.get_kpi(db, id_kpi)
        if not db_kpi:
            return None
        
        update_data = kpi.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_kpi, key, value)
            
        db.commit()
        db.refresh(db_kpi)
        return db_kpi

    def delete_kpi(self, db: Session, id_kpi: str):
        db_kpi = self.get_kpi(db, id_kpi)
        if db_kpi:
            db.delete(db_kpi)
            db.commit()
        return db_kpi

kpi_service = KpiService()
