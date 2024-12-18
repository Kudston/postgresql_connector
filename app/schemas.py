from pydantic import BaseModel
from typing import List, Dict

class ColumnDefinition(BaseModel):
    name: str
    type: str
    unique: bool = False
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

class TableDataUpdateIn(BaseModel):
    table_name: str
    id: int
    data: Dict

class SingleTableDataOut(BaseModel):
    data: Dict

class TableDataOut(BaseModel):
    data: List[Dict]

class DeleteResponse(BaseModel):
    detail: str