from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from typing import Union
from config import Settings
from schemas import TableSchema, ColumnDefinition, TableCreateOut, TableDataIn, TableDataOut, DeleteTableResponse
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
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.create_table(table_data)
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

    def get_data(
        self,
        table_name: str
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.get_table_data(table_name=table_name)
            
            data = {
                "data":result
            }

            return success_service_result(TableDataOut.model_validate(data))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)
        
    def delete_table(
        self,
        table_name: str
    )->Union[ServiceResult, Exception]:
        try:
            result = self.crud.drop_table_by_name(table_name=table_name)
            return success_service_result(DeleteTableResponse.model_validate(result))
        except Exception as raised_exception:
            return failed_service_result(raised_exception)