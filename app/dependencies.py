from uuid import uuid4

from sqlalchemy.orm import Session
from fastapi import Depends
from config import Settings
from database import get_db_sess
from services import DataBaseService
from service_results import get_settings

def initiate_database_service(
    db: Session = Depends(get_db_sess),
    app_settings: Settings = Depends(get_settings),
):
    return DataBaseService(db=db, app_settings=app_settings)
