from contextlib import asynccontextmanager
from database import engine, open_db_connections, close_db_connections
from fastapi import FastAPI, APIRouter, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from schemas import TableCreateOut, TableSchema, TableDataOut, TableDataIn, DeleteResponse, SingleTableDataOut, TableDataUpdateIn
from dependencies import initiate_database_service
from service_results import handle_result
from services import DataBaseService
from models import Base
from config import Settings
from uuid import uuid4

@asynccontextmanager
async def lifespan(app: FastAPI):
    ##open db connections
    open_db_connections()
    yield
    ##close db connections
    close_db_connections()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_credentials= True,
    allow_headers=["*"],
)
 
settings = Settings()

@app.get("/")
def welcome():
    return {"detail":"Welcome ..."}

@app.post("/create-table", response_model=TableCreateOut)
async def create_table(
    table_data: TableSchema,
    generate_datetime_columns: bool = Query(False, description="Automatically adds created_at and updated_at datetime columns."),
    autogenerate_id_column: bool = Query(False, description="Autogenerate id column."),
    db_service: DataBaseService = Depends(initiate_database_service)
):
    result = db_service.create_table(
        table_data = table_data,
        autogenerate_id_column=autogenerate_id_column,
        generate_datetime_columns=generate_datetime_columns,
    )
    return handle_result(result, TableCreateOut)

@app.post("/insert-data", response_model=TableDataOut)
async def insert_data(
    data: TableDataIn,
    db_service: DataBaseService = Depends(initiate_database_service)
):
    result = db_service.insert_data(data=data)
    return handle_result(result, TableDataOut)

@app.get("/get-data-by-id", response_model=SingleTableDataOut)
def get_table_data_id(
    table_name: str = Query(),
    data_id: str = Query(),
    db_service: DataBaseService = Depends(initiate_database_service)
):
    result = db_service.get_data_by_id(
        table_name=table_name,
        data_id=data_id
    )
    return handle_result(result, SingleTableDataOut)

@app.get("/get-datas", response_model=TableDataOut)
def get_table_data(
    table_name: str = Query(), 
    skip: int = Query(default=0), 
    limit: int = Query(default=100), 
    order_direction: str = Query(default="asc"), 
    order_by: str = Query(default='created_at'),
    db_service: DataBaseService = Depends(initiate_database_service)
):
    result = db_service.get_datas(
        table_name=table_name,
        skip=skip,
        limit=limit,
        order_direction=order_direction,
        order_by=order_by
    )
    return handle_result(result, TableDataOut)

@app.get("/send-sql-command")
def send_sql_command(
    sql_command: str,
    db_service: DataBaseService = Depends(initiate_database_service)
):
    result = db_service.send_raw_sql_command(sql_command=sql_command)
    return result


@app.put("/update-record", response_model=SingleTableDataOut)
def update_table_data(
    data: TableDataUpdateIn,
    db_service: DataBaseService = Depends(initiate_database_service)
):
    result = db_service.update_data(data=data)
    return handle_result(result, expected_schema=SingleTableDataOut)

@app.delete("/delete-data", response_model=DeleteResponse)
def delete_table_data(
    table_name: str,
    data_id: str,
    db_service: DataBaseService = Depends(initiate_database_service)
):
    result = db_service.delete_record(
        table_name=table_name,
        data_id=data_id
    )
    return handle_result(result, expected_schema=DeleteResponse)

@app.delete("/delete-table", response_model=DeleteResponse)
def delete_table(
    table_name: str = Query(),
    db_service: DataBaseService = Depends(initiate_database_service)
):
    result = db_service.delete_table(table_name)
    return handle_result(result, expected_schema=DeleteResponse)