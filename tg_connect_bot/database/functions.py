import sqlite3
import decouple

from typing import Union, List

path_to_db = decouple.config('PATH_TO_DATABASE')

async def select_function(columns: List[str], table: str, conditions: Union[List[str], None], result: Union[str, None]) -> Union[list, tuple]:
    """
    Executes an SQL query and returns the result based on the value of `result`.
    :param columns: A list of columns to select.
    :param table: The name of the table.
    :param conditions: A list of conditions for the WHERE clause.
    :param result: Determines the result format ('all' for fetchall or 'one' for fetchone).

    :return: The result of the SQL query as a list (if result == 'all') or a tuple (if result == 'one').
    """
    columns = ', '.join(columns)
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ''
    try:
        with sqlite3.connect(path_to_db) as conn:
            cur = conn.cursor()
            query = f"SELECT {columns} FROM {table}{where_clause}"
            cur.execute(query)
            if result == 'one':
                result = cur.fetchone()
            else:
                result = cur.fetchall()
            cur.close()
            return result
    except sqlite3.Error as e:
            print(e)


async def update_function(table: str, set_values: dict, conditions: Union[List[str], None]) -> None:
    """
    Executes an SQL UPDATE query to update records in the table.

    :param table: The name of the table to update.
    :param set_values: A dictionary with "column: value" pairs for setting new values.
    :param conditions: A list of conditions for the WHERE clause.

    :return: None.
    """
    set_clause = ", ".join([f"{column} = ?" for column in set_values.keys()])
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ''
    try:
        with sqlite3.connect(path_to_db) as conn:
            cur = conn.cursor()
            query = f"UPDATE {table} SET {set_clause}{where_clause}"
            values = list(set_values.values())
            cur.execute(query, values)
            conn.commit()
            cur.close()
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении записей: {e}")


async def insert_function(table: str, insert_values: dict) -> None:
    """
    Executes an SQL INSERT query to insert new records into the table.

    :param table: The name of the table for insertion.
    :param insert_values: A dictionary with "column: value" pairs for inserting new records.

    :return: None.
    """
    insert_clause = ", ".join(insert_values.keys())
    placeholders = ", ".join(["?" for _ in insert_values])
    try:
        with sqlite3.connect(path_to_db) as conn:
            cur = conn.cursor()
            query = f"INSERT INTO {table} ({insert_clause}) VALUES ({placeholders})"
            values = list(insert_values.values())
            cur.execute(query, values)
            conn.commit()
            cur.close()
    except sqlite3.Error as e:
        print(f"Ошибка при вставке записей: {e}")


async def delete_function(table: str, conditions: List[str]) -> None:
    """
    Executes an SQL DELETE query to delete records from the table.

    :param table: The name of the table for deletion.
    :param conditions: A list of conditions for the WHERE clause.

    :return: None.
    """
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ''
    try:
        with sqlite3.connect(path_to_db) as conn:
            cur = conn.cursor()
            query = f"DELETE FROM {table}{where_clause}"
            cur.execute(query)
            conn.commit()
            cur.close()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении записей: {e}")




async def select_function_pay(columns: List[str], table: str, conditions: Union[List[str], None], result: Union[str, None]) -> Union[list, tuple]:
    """
    Executes an SQL query and returns the result based on the value of `result`.
    :param columns: A list of columns to select.
    :param table: The name of the table.
    :param conditions: A list of conditions for the WHERE clause.
    :param result: Determines the result format ('all' for fetchall or 'one' for fetchone).

    :return: The result of the SQL query as a list (if result == 'all') or a tuple (if result == 'one').
    """
    columns = ', '.join(columns)
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ''
    where_clause += " ORDER BY id DESC LIMIT 1"
    try:
        with sqlite3.connect(path_to_db) as conn:
            cur = conn.cursor()
            query = f"SELECT {columns} FROM {table}{where_clause}"
            cur.execute(query)
            if result == 'one':
                result = cur.fetchone()
            else:
                result = cur.fetchall()
            cur.close()
            return result
    except sqlite3.Error as e:
            print(e)


async def update_function_pay(table: str, set_values: dict, conditions: Union[List[str], None]) -> None:
    """
    Executes an SQL UPDATE query to update records in the table.

    :param table: The name of the table to update.
    :param set_values: A dictionary with "column: value" pairs for setting new values.
    :param conditions: A list of conditions for the WHERE clause.

    :return: None.
    """

    """
        UPDATE transactions 
        SET status = 'complete' 
        WHERE tg_id = ? 
        AND id = (
            SELECT id 
            FROM transactions 
            WHERE tg_id = ? 
            ORDER BY id DESC 
            LIMIT 1
        )
        AND status = 'open'
    """


    set_clause = ", ".join([f"{column} = ?" for column in set_values.keys()])
    # where_clause = " WHERE " + " AND ".join(conditions) if conditions else ''
    where_clause = f""" WHERE {conditions[0]} AND id = ( SELECT id FROM {table} WHERE {conditions[0]} ORDER BY id DESC LIMIT 1 ) AND status = 'open'"""
    try:
        with sqlite3.connect(path_to_db) as conn:
            cur = conn.cursor()
            query = f"UPDATE {table} SET {set_clause} {where_clause}"
            values = list(set_values.values())
            cur.execute(query, values)
            conn.commit()
            cur.close()
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении записей: {e}")


async def insert_function_pay(table: str, insert_values: dict) -> None:
    """
    Executes an SQL INSERT query to insert new records into the table.

    :param table: The name of the table for insertion.
    :param insert_values: A dictionary with "column: value" pairs for inserting new records.

    :return: None.
    """
    insert_clause = ", ".join(insert_values.keys())
    placeholders = ", ".join(["?" for _ in insert_values])
    try:
        with sqlite3.connect(path_to_db) as conn:
            cur = conn.cursor()
            query = f"INSERT INTO {table} ({insert_clause}) VALUES ({placeholders})"
            values = list(insert_values.values())
            cur.execute(query, values)
            conn.commit()
            cur.close()
    except sqlite3.Error as e:
        print(f"Ошибка при вставке записей: {e}")


async def select_function_email(columns: List[str], table: str, email: Union[List[str], None], result: Union[str, None]) -> Union[list, tuple]:
    """
    Executes an SQL query and returns the result based on the value of `result`.
    :param columns: A list of columns to select.
    :param table: The name of the table.
    :param conditions: A list of conditions for the WHERE clause.
    :param result: Determines the result format ('all' for fetchall or 'one' for fetchone).

    :return: The result of the SQL query as a list (if result == 'all') or a tuple (if result == 'one').
    """
    columns = ', '.join(columns)
    try:
        with sqlite3.connect(path_to_db) as conn:
            cur = conn.cursor()
            query = f"SELECT {columns} FROM {table} WHERE email = ?"
            cur.execute(query, (email,))
            if result == 'one':
                result = cur.fetchone()
            else:
                result = cur.fetchall()
            cur.close()
            return result
    except sqlite3.Error as e:
            print(e)

