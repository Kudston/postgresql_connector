from pydantic import BaseModel
from typing import List, Dict

class ColumnDefinition(BaseModel):
    name: str
    type: str
    primary_key: bool = False
    nullable: bool = True

class TableSchema(BaseModel):
    table_name: str
    columns: List[ColumnDefinition]

class TableCreateOut(BaseModel):
    message: str
    columns: List[ColumnDefinition]

class TableDataIn(BaseModel):
    table_name: str
    data: Dict

class TableDataOut(BaseModel):
    data: List[Dict]

class DeleteTableResponse(BaseModel):
    detail: str

