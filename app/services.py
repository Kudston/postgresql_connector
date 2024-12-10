from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import UUID
from typing import Union
from config import Settings
from schemas import (
    TableSchema, 
    ColumnDefinition, 
    TableCreateOut, 
    TableDataIn, 
    TableDataOut, 
    DeleteResponse,
    TableDataUpdateIn, 
    SingleTableDataOut)

from crud import DataBaseCrud
from service_results import ServiceResult, success_service_result, failed_service_result

class DataBaseService:
    def __init__(
        self,
        db: Session,
        app_settings: Settings
    ) -> None:
        self.crud = DataBaseCrud(db=db)
        self.app_settings = app_settings
        
    def create_table(
        self,
        table_data: TableSchema,
        generate_datetime_columns: bool,
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.create_table(
                table_data=table_data, 
                generate_datetime_columns=generate_datetime_columns
            )
            result_dict = {
                'message':result['message'],
                'columns':[ColumnDefinition.model_validate(col) for col in result['columns']]
            }
            return success_service_result(TableCreateOut.model_validate(result_dict))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)
    
    def insert_data(
        self,
        data: TableDataIn
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.insert_data(table_name=data.table_name, data=data.data)

            return success_service_result(TableDataOut.model_validate(result))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)

    def get_datas(
        self,
        table_name: str, 
        skip: int = 0, 
        limit: int = 100, 
        order_direction: str = 'asc', 
        order_by: str = 'created_at'
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.get_table_datas(
                table_name=table_name,
                skip=skip,
                limit=limit,
                order_direction=order_direction,
                order_by=order_by
            )
            
            data = {
                "data":result
            }

            return success_service_result(TableDataOut.model_validate(data))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)

    def get_data_by_id(
        self,
        table_name,
        data_id
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.get_data_by_id(
                table_name=table_name, record_id=data_id
            )
            data = {
                "data":result
            }
            return success_service_result(SingleTableDataOut.model_validate(data))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)

    def update_data(
        self,
        data: TableDataUpdateIn
    ) -> Union[ServiceResult, Exception]:
        try:
            result = self.crud.update_table_record_by_id(
                table_name=data.table_name, 
                id=data.id,
                data=data.data
            )
            data = {
                'data':result
            }
            return success_service_result(SingleTableDataOut.model_validate(data))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)

    def delete_record(
        self,
        table_name: str,
        data_id: UUID
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.delete_data_from_table(
                table_name=table_name,
                record_id=data_id
            )
            result = {
                "detail":f"Deleted {result} row with id: {data_id}"
            }
            return success_service_result(DeleteResponse.model_validate(result))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)

    def delete_table(
        self,
        table_name: str
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.drop_table_by_name(table_name=table_name)
            return success_service_result(DeleteResponse.model_validate(result))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)
    
    def send_raw_sql_command(
        self,
        sql_command: str
    ):
        try:
            result = self.crud.send_raw_sql_command(sql_command)
            return result
        except Exception as raised_exception:
            return str(raised_exception)