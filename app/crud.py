from sqlalchemy.types import (
    String,
    Integer,
    Boolean,
    DateTime,
    Float,
)
from typing import Dict
from schemas import TableSchema
from sqlalchemy import MetaData, Table, Column, inspect, text, func
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
                Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
                Column('created_at', DateTime(timezone=True), server_default=func.now()),
                Column('updated_at', DateTime(timezone=True), 
                    server_default=func.now(),
                    onupdate=func.now())
                ]

            for col in table_data.columns:
                if col.type.lower() not in type_mapping:
                    raise Exception(
                        f"Unsupported data type: {col.type}. Supported types are: {list(type_mapping.keys())}"
                    )
                
                column = Column(
                    col.name,
                    type_mapping[col.type.lower()](),
                    nullable=col.nullable,
                    unique=col.unique
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
        
    def get_table_data(
        self, 
        table_name: str, 
        skip: int = 0, 
        limit: int = 100, 
        order_direction: str = 'asc', 
        order_by: str = 'created_at'
    ):
        table = self.get_table_structure(table_name)
        column_names = [col.name for col in table.columns]
        
        if order_by not in column_names:
            raise ValueError(f"Invalid order_by column: {order_by}")
        
        # Validate order_direction
        if order_direction.lower() not in ['asc', 'desc']:
            raise ValueError("Order direction must be 'asc' or 'desc'")
        
        query = self.db.query(table)
        
        order_column = getattr(table.c, order_by)
        if order_direction.lower() == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        query = query.offset(skip).limit(limit)
        
        # Execute and convert to dict
        results = query.all()

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