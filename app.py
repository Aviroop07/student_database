import streamlit as st
import mysql.connector 
from mysql.connector import DatabaseError, IntegrityError, InternalError, Error
import pandas as pd



@st.cache_resource
def create_connection():
    try:
        connection = mysql.connector.connect(
            host = st.secrets['mysql']['host'],
            database = st.secrets['mysql']['database'],
            user = st.secrets['mysql']['user'],
            password = st.secrets['mysql']['password']
        )

        if connection.is_connected():
            db_Info = connection.get_server_info()
            st.write("Connected to MySQL database...", db_Info)
            # cursor = connection.cursor()
            # cursor.execute("select database();")
            # record = cursor.fetchone();
            # st.write("Your connected to database :", record[0])
            return connection
    except Error as e:
        st.write("Error while connecting to MySQL", e)
        return None
    

def insert_data(connection, roll, name):    
    cursor = connection.cursor()
    cursor.execute(
        'insert into student (roll, name) values (%s, %s);',
        (roll, name)
    )
    connection.commit()


def read_data(connection):
    if st.session_state.edited == False and st.session_state.current_data is not None:
        return st.session_state.current_data
    try:
        cursor = connection.cursor()
        cursor.execute('select * from student')
        result = cursor.fetchall()
        payld = {"roll" : [r[0] for r in result],"name" : [r[1] for r in result]}
        df = pd.DataFrame(payld, columns = ['roll', 'name'])
        return df
    except Error as e:
        st.write("Error while reading data", e)
        return None

    
def delete_data(connection, roll):
    cursor = connection.cursor()
    cursor.execute(
        'delete from student where roll = %s;',
        (roll,)
    )
    connection.commit()
    if cursor.rowcount == 0:
        raise IntegrityError("No data deleted")


def edit_data(connection, roll, name):
    cursor = connection.cursor()
    cursor.execute(
        'update student set name = %s where roll = %s;',
        (name, roll)
    )
    connection.commit()
    if cursor.rowcount == 0:
        raise IntegrityError("No data updated")


# components from here ---> 

if 'edited' not in st.session_state:
    st.session_state.edited = True

if 'current_data' not in st.session_state:
    st.session_state.current_data = None


st.title("Student Database App")
connection = create_connection()
if connection:
    st.session_state.current_data = read_data(connection)
    st.session_state.edited = False


roll = st.number_input('Roll',placeholder='Enter your roll here',min_value=100,step=1,max_value=1000)
name = st.text_input('Name',placeholder='Enter your name here')
insert_button = st.button('Insert Data')
insert_status = st.empty()
read_button = st.button('Read Data')
read_status = st.empty()
show_tables = st.empty()
delete_roll = st.number_input('Roll',placeholder='Enter roll to delete',min_value=100,step=1,max_value=1000)
delete_button = st.button('Delete Entry')
delete_status = st.empty()
edit_roll = st.number_input('Roll',placeholder='Enter roll to edit',min_value=100,step=1,max_value=1000)
edit_name = st.text_input('Name',placeholder='Enter new name here')
edit_button = st.button('Edit Data')
edit_status = st.empty()


if insert_button:
    if name == "":
        insert_status.error('Name cannot be empty')
    else:
        try:
            insert_data(connection, roll, name)
            st.session_state.edited = True
            insert_status.success('Data inserted successfully')
        except IntegrityError as e:
            insert_status.error('Duplicate entry')
        except Error as e:
            insert_status.error('Error while inserting data', e)


if read_button:
    st.session_state.current_data = read_data(connection)
    if st.session_state.current_data is not None:
        st.session_state.edited = False
        read_status.success('Fetched data successfully')
        show_tables.dataframe(st.session_state.current_data)
    else:
        read_status.error('Error while reading data')


if delete_button:
    try:
        delete_data(connection, delete_roll)
        st.session_state.edited = True
        delete_status.success('Entry deleted successfully')
    except IntegrityError as e:
        delete_status.error(e)
    except Error as e:
        delete_status.error('Error while deleting entry')

if edit_button:
    try:
        edit_data(connection, edit_roll, edit_name)
        st.session_state.edited = True
        edit_status.success('Entry edited successfully')
    except IntegrityError as e:
        edit_status.error(e)
    except Error as e:
        edit_status.error('Error while editing entry')