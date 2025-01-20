#Railway reservation system using SQLite and sreamlit python
import streamlit as st
import sqlite3
import pandas as pd

#import database
conn=sqlite3.connect('railway.db')
current_page='Login or Sign up'
c=conn.cursor()

#creating function to create db
def create_db():
    c.execute("Create table if not exists users (username TEXT, password TEXT)")
    c.execute("Create table if not exists employees (emp_id TEXT, password TEXT, designation TEXT)")
    c.execute("Create table if not exists Trains(train_number TEXT, train_name TEXT, start_destination TEXT, end_destination TEXT)")
create_db()
    
#search train
def search_train(train_number):
    train_query=c.execute("SELECT* FROM Trains WHERE train_number=?",(train_number,))
    train_data=train_query.fetchone()
    
    return train_data

#train destination search
def train_destination(start_destination, end_destination):
    train_query=c.execute ("SELECT * FROM trains WHERE start_destination=?, ending_destination=?",(start_destination,end_destination))
    train_data=train_query.fetchall()
    return train_data


#add train
def add_train(train_number, train_name, departure_date, start_destination, end_destination ):
    c.execute("insert into trains(train_number, train_name, departure_date, start_destination, end_destination) values(?,?,?,?,?)",
              (train_number, train_name, departure_date, start_destination, end_destination) )
    
    conn.commit()
    create_seat_table(train_number)
    
#creating seat table for train
def create_seat_table(train_number):
    c.execute(f"create table if not exists seats_{train_number}"
              f"(seat_number INTEGER PRIMARY KEY,"
              f"seat_type TEXT"
              f"booked INTEGER,"
              f"passenger_name TEXT"
              f"passenger_age INTEGER"
              f"passenger_gender TEXT)")
    for i in range(1,51):
        val=categorize_seat(i)
        c.execute(f'''INSERT INTO seats_{train_number}(seat_number, seat_type, booked, passenger_name, passenger_age, passenger_gender) VALUES(?,?,?,?,?,?);''', (i,val,0,''','''))
        conn.commit()
        
#allocate next availabele seat
def allocate_next_available_seat(train_number,seat_type):
    seat_query=c.execute(f"SELECT seat_number FROM seat_{train_number} WHERE booked=0 and seat_type=?"
                         f"ORDER BY seat_number ASC",(seat_type,))
    result= seat_query.fetchall()
    if result:
        return[0]
    
#categorize seat in train
def categorize_seat(seat_number):
    if(seat_number%10) in [0,4,5,9]:
        return "Window"
    elif (seat_number % 10) in [2,3,6,7]:
        return "Aisle"
    else:
        return "Middle"
    
#view available seats 
def view_seats(train_number):
    train_query=c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data=train_query.fetchone()
    if train_data:
        seat_query=c.execute(f'''SELECT 'Number: '|| seat_number, '\n Type: '||seat_type,'\n Name:'||passenger_name,'\n Age:'||passenger_Age,'\n Gender:'||passenger_gender as Details , booked FROM seats_{train_number} ORDER BY seat_number ASC''')
        
        result=seat_query.FETCHALL()
        if result:
            st.dataframe(data=result)
            
#book tickets
def book_tickets(train_number, passenger_name, passenger_age, passenger_gender, seat_type):
    train_query=c.execute("SELECT * FROM trains WHERE train_number=?",(train_number,))
    train_data=train_query.fetchone()
    
    if train_data:
        seat_number=allocate_next_available_seat(train_number,seat_type)
        if seat_number:
            c.execute(f"UPDATE seats_{train_number} SET booked=1, seat_type=?, passenger_name=?, passenger_age=?, passenger_gender=?"
                      f"WHERE seat_number=?", (seat_type, passenger_name, passenger_age, passenger_gender))
            conn.commit()
            st.success(f"Booked Successfully!!")
            
#cancel tickets
def cancel_tickets(train_number, seat_number):
    train_query=c.execute("SELECT* FROM trains WHERE train_number=?", (train_number,))
    train_data=train_query.fetchone()
    
    # if train_data:
    #     c.execute(f"UPDATE seats_{train_number} SET booked=0, passenger_name=' ', passenger_age=' ',passenger_gender='' WHERE seat_number=?"(seat_number))
        
    #     conn.commit()
    #     st.success(f"Canceled Successfuly!!")

def cancel_tickets(train_number, seat_number):
    c.execute(f"""
        UPDATE seats_{train_number}
        SET booked=0, passenger_name='', passenger_age=0, passenger_gender=''
        WHERE seat_number=?
    """, (seat_number,))
    conn.commit()
    st.success("Ticket canceled successfully!")


#delete train
def delete_train(train_number, departure_date):
    train_query=c.execute(" SELECT * FROM  trains WHERE train_number=?",(train_number))
    train_data=train_query.fetchone()
    
    if train_data:
        c.execute("DELETE FROM trains WHERE train_number=? AND departure_date=?" ,(train_number,departure_date))
        
        conn.commit()
        st.success(f"Deleted Train Successfully!!!")
        
#apply all functions
def train_functions():
    st.title('Train Administrator')
    functions=st.sidebar.selectbox("Select train function",["Add train","view train","Search train","Delete train","Book ticket","Cancel Ticket","View Seats"])
    if functions=="add train":
        st.header("add new train")
        with st.form(key="new_train_details"):
            train_number=st.text_input("train number")
            train_name=st.text_input("train name")
            departure_date=st.text_input("date")
            start_destination=st.text_input("start destination")
            end_destination=st.text_input("end destination")
            submitted=st.form_submit_button('add train')
            
        if submitted and train_name!="" and train_number!='' and start_destination !="" and end_destination!="":
            add_train(train_number, train_name, departure_date, start_destination, end_destination )
            
            st.success("Train added successfully!")
            
    elif functions=="view train":
        st.title("View all trains")
        train_query=c.execute("SELECT * FROM trains")
        trains=train_query.fetchall()
        
    elif functions=="book tickets":
        st.title("Book train tickets")
        train_number=st.text_input("Enter train number:")
        seat_type=st.selectbox("seat_type",["aisle","window","middle"],index=0)
        passenger_name=st.text_input("Enter passenger name:")
        passenger_age=st.number_input("Enter passenger age:",min_value=1)
        passenger_gender=st.selectbox("Enter passenger Gender:",["Male","Female","Other"],index=0)
        
        if st.button("book ticket"):
            if train_number and passenger_name and passenger_gender and passenger_age:
                book_tickets(train_number, passenger_name, passenger_age, passenger_gender, seat_type)
                
    elif functions=="cancel_tickets":
        st.title("Cancel ticket")
        train_number=st.text_input("Enter train number")
        seat_number=st.text_input("Enter seat number",min_value=1)
        if st.button("cancel_tickets"):
            if train_number and seat_number:
                cancel_tickets(train_number,seat_number)
                
    elif functions=="view seats":
        st.title("view seats")
        train_number=st.text_input("Enter train number")
        if st.button("submit"):
            view_seats(train_number)
            
    elif functions=="delete train":
        st.title="delete train"
        train_number=st.text_input("Enter train number")
        departure_date=st.date_input("Enter date")
        
        if st.button("delete train"):
            if train_number:
                c.execute(f"DROP TABLE IF EXISTS seats_{train_number}")
                delete_train(train_number,departure_date)