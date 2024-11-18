from sqlalchemy.types import (
    String,
    Integer,
    Boolean,
    DateTime,
    Float,
)
from typing import Dict
from schemas import TableSchema
from sqlalchemy import MetaData, Table, Column, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


type_mapping = {
    "string": String,
    "integer": Integer,
    "boolean": Boolean,
    "datetime": DateTime,
    "float": Float
}

class DataBaseCrud:
    def __init__(self, db) -> None:
        self.db: Session = db

    def get_table_structure(self, table_name: str):
        try:
            inspector = inspect(self.db.bind)
            if not inspector.has_table(table_name):
                raise ValueError(f"Table '{table_name}' does not exist")
            
            metadata = MetaData()

            table = Table(table_name, metadata, autoload_with=self.db.bind)

            return table
        except Exception as raised_exception:
            print(str(raised_exception))
            raise raised_exception

    def create_table(
        self,
        table_data: TableSchema
    ):
        try:
            inspector = inspect(self.db.bind)
            if inspector.has_table(table_data.table_name):
                raise Exception(f"Table '{table_data.table_name}' already exists")
            
            # Ensure more than one column
            if len(table_data.columns) <= 1:
                raise Exception(f"Table must have more than one column. Current column count: {len(table_data.columns)}")
            
            metadata = MetaData()

            columns = [
                # Add UUID4 column as primary key
                Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4)
            ]

            for col in table_data.columns:
                if col.type.lower() not in type_mapping:
                    raise Exception(
                        f"Unsupported data type: {col.type}. Supported types are: {list(type_mapping.keys())}"
                    )
                
                column = Column(
                    col.name,
                    type_mapping[col.type.lower()](),
                    primary_key=col.primary_key,
                    nullable=col.nullable
                )
                columns.append(column)
            
            # Create table
            table = Table(
                table_data.table_name,
                metadata,
                *columns
            )
            
            # Create the table in the database
            metadata.create_all(self.db.bind)

            return {
                "message": f"Table '{table_data.table_name}' created successfully",
                "columns": [{'name': 'id', 'type': 'uuid', 'primary_key':'true', 'nullable':'true'}] + table_data.columns
            }
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise
    
    def insert_data(self, table_name: str, data: Dict):
        try:
            if not table_name.isalnum():
                raise ValueError("Invalid table name")
            
            inspector = inspect(self.db.bind)
            if not inspector.has_table(table_name):
                raise ValueError(f"Table '{table_name}' does not exist")

            table = self.get_table_structure(table_name)

            valid_columns = {col.name for col in table.columns}
            invalid_columns = set(data.keys()) - valid_columns

            if invalid_columns:
                raise ValueError(f"Invalid columns: {invalid_columns}")

            with self.db.begin():
                filtered_data = {k: v for k, v in data.items() if k in valid_columns}
                filtered_data['id'] = uuid4()
                result = self.db.execute(table.insert().values(**filtered_data))

            return {
                "data": [filtered_data]
            }
        except SQLAlchemyError as db_error:
            raise ValueError(f"Database error: {str(db_error)}")
        except Exception as e:
            raise ValueError(str(e))
        
    def get_table_data(self, table_name:str):
        table = self.get_table_structure(table_name)
        query = self.db.query(table)
        
        column_names = [col.name for col in table.columns]
        
        results =  query.all()
        return [dict(zip(column_names, row)) for row in results]
        
    
    def drop_table_by_name(self,table_name: str):
        try:
            inspector = inspect(self.db.bind)
            if not inspector.has_table(table_name):
                raise ValueError(f"Table '{table_name}' does not exist")

            drop_query = text(f'DROP TABLE IF EXISTS "{table_name}"')
            self.db.execute(drop_query)
            self.db.commit()
            return {"detail": f"Table '{table_name}' dropped successfully"}
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error dropping table: {str(e)}")