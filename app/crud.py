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
                Column('id', Integer, primary_key=True, autoincrement=True),
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
                "columns": [{'name': 'id', 'type': 'integer', 'primary_key':'true', 'nullable':'false'}] + table_data.columns
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
                # filtered_data['id'] = uuid4()
                result = self.db.execute(table.insert().values(**filtered_data))

            return {
                "data": [filtered_data]
            }
        except SQLAlchemyError as db_error:
            raise ValueError(f"Database error: {str(db_error)}")
        except Exception as e:
            raise ValueError(str(e))
        
    def get_table_datas(
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
        
    def update_table_record_by_id(self, table_name: str, id: UUID, data: Dict):
        try:
            if not table_name.isalnum():
                raise ValueError("Invalid table name")
            
            inspector = inspect(self.db.bind)
            if not inspector.has_table(table_name):
                raise ValueError(f"Table '{table_name}' does not exist")

            table = self.get_table_structure(table_name)

            valid_columns = {col.name for col in table.columns}

            invalid_columns = set(data.keys()) - valid_columns - {'id', 'created_at'}

            if invalid_columns:
                raise ValueError(f"Invalid columns: {invalid_columns}")

            filtered_data = {
                k: v for k, v in data.items() 
                if k in valid_columns and k not in ['id', 'created_at', 'updated_at']
            }

            if not filtered_data:
                raise ValueError("No valid columns to update")

            with self.db.begin():
                update_stmt = (
                    table.update()
                    .where(table.c.id == id)
                    .values(**filtered_data)
                )
                result = self.db.execute(update_stmt)

                if result.rowcount == 0:
                    raise ValueError(f"No record found with id {id}")
            
            with self.db.begin():
                data = (table.select()
                .where(table.c.id == id)
                )
                data = self.db.execute(data)
            column_names = [col.name for col in table.columns]
            data = data.first()
            return dict(zip(column_names,data))
        except SQLAlchemyError as db_error:
            raise ValueError(f"Database error: {str(db_error)}")
        except Exception as e:
            raise ValueError(str(e))        

    def get_data_by_id(self, table_name, record_id):
        try:
            if not table_name.isalnum():
                raise ValueError("Invalid table name")
            
            inspector = inspect(self.db.bind)
            if not inspector.has_table(table_name):
                raise ValueError(f"Table '{table_name}' does not exist")

            table = self.get_table_structure(table_name)

            with self.db.begin():
                data = (table.select()
                .where(table.c.id == record_id)
                )
                data = self.db.execute(data)
            column_names = [col.name for col in table.columns]
            data = data.first()
            return dict(zip(column_names,data))
        except SQLAlchemyError as db_error:
            raise ValueError(f"Database error: {str(db_error)}")
        except Exception as e:
            raise ValueError(str(e))

    def delete_data_from_table(
        self,
        table_name,
        record_id
    ):
        try:
            if not table_name.isalnum():
                raise ValueError("Invalid table name")
            
            inspector = inspect(self.db.bind)
            if not inspector.has_table(table_name):
                raise ValueError(f"Table '{table_name}' does not exist")

            table = self.get_table_structure(table_name)

            with self.db.begin():
                delete_stmt = (
                    table.delete()
                    .where(table.c.id == record_id)
                )
                result = self.db.execute(delete_stmt)

                if result.rowcount == 0:
                    raise ValueError(f"No record found with id {id}")

            return result.rowcount
        except SQLAlchemyError as db_error:
            raise ValueError(f"Database error: {str(db_error)}")
        except Exception as e:
            raise ValueError(str(e))        

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

    def send_raw_sql_command(
        self,
        sql_command: str,
    ):
        try:
            if not sql_command.strip():
                raise ValueError("SQL command cannot be empty")
            
            with self.db.begin():
                result = self.db.execute(text(sql_command))
            
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = result.keys()
                    converted_rows = [
                    zip(columns, row)
                    for row in rows
                    ]

                    print(converted_rows)

                    return converted_rows
                else:
                    return {
                        "rowAffected": result.rowcount,
                    }        
        except Exception as raised_exception:
            self.db.rollback()
            raise ValueError(f"Error executing SQL command: {str(raised_exception)}")