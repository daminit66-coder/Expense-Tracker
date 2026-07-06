import psycopg2
import streamlit as st

from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cursor = conn.cursor()

print("Database Connected Successfully")
'''query="""
insert into expense
(Product_Name,category,price,Quantity ,Payment_Method,Buy_From,Purchase_Date )
values(%s,%s,%s,%s,%s,%s,%s)
"""
values=(
    "shampoo","haircare",400,1,"Gpay","online","29-06-2026"
)
cursor.execute(query, values)
conn.commit()
cursor.execute("select * from expense")
row=cursor.fetchall()
for row in row:
    print(row)'''''
def add():
    name=input("Product Name :")
    category=input("Category :")
    price=input("Price :")
    quantity=input("Quantity :")
    payment=input("Payment Method :")
    buy=input("Buy From :")
    date=input("Purchase Date DD-MM-YYYY:")
    query="""
    insert into expense
    (Product_Name,category,price,Quantity ,Payment_Method,Buy_From,Purchase_Date )
    values(%s,%s,%s,%s,%s,%s,%s)
    """
    values=(name,category,price,quantity ,payment,buy,date)
    cursor.execute(query,values)
    conn.commit()
    print("Expense Add Successfully !")
def all():
    cursor.execute("select * from expense")
    row=cursor.fetchall()
    for row in row:
        print(row)
def Row():
    name=input("Enter Product Name :")
    query=""" select * from expense where  Product_Name=%s"""
    cursor.execute(query,(name,))
    row=cursor.fetchall()
    for row in row:
        print(row)


def column():
    print("="*20)
    print("1.Product Name")
    print("="*20)
    print("2.category")
    print("="*20)
    print("3.price")
    print("="*20)
    print("4.Quantity")
    print("="*20)
    print("5.Payment Method")
    print("="*20)
    print("6.Buy from")
    print("="*20)
    print("7.Purchase Date") 
    print("="*20)
    col_name=int(input("Enter your choice :"))
    if col_name==1:
        query=""" select Product_Name from expense """
        cursor.execute(query)
        row=cursor.fetchall()
        for row in row:
            print(row[0])


    elif col_name == 2:
        query=""" select category from expense """
        cursor.execute(query)
        row=cursor.fetchall()
        for row in row:
            print(row[0])


    elif col_name == 3:
        query=""" select price from expense"""
        cursor.execute(query)
        row=cursor.fetchall()
        for row in row:
            print(row[0])


    elif col_name == 4:
        query=""" select Quantity from expense"""
        cursor.execute(query)
        row=cursor.fetchall()
        for row in row:
            print(row[0])
    elif col_name == 5:
        query=""" select Payment_Method from expense"""
        cursor.execute(query)
        row=cursor.fetchall()
        for row in row:
            print(row[0])
    elif col_name == 6:
        query=""" select Buy_from from expense"""
        cursor.execute(query)
        row=cursor.fetchall()
        for row in row:
            print(row[0]) 
    elif col_name == 7:
        query=""" select Purchase_Date from expense"""
        cursor.execute(query)
        row=cursor.fetchall()
        for row in row:
            print(row[0])                       



    


def view():
    while True:
        print("---1.All Entery :---")
        print("---2.Particular row :--- ")
        print("---3.Particular Column :---")
        print("4.Go back!")
        ch=int(input("choice :"))
        if ch==1:
            all()
        elif ch==2:
            Row()
        elif ch==3:
            column()
        elif ch==4:
            break

def update():
    
    while True:
        
        P_name=(input("Enter the product name :"))
        print("which field would you like to update?")
        print("="*20)
        print("Product_Name")
        print("="*20)
        print("category")
        print("="*20)
        print("price")
        print("="*20)
        print("Quantity")
        print("="*20)
        print("Payment Method")
        print("="*20)
        print("Buy from")
        print("="*20)
        print("Purchase Date") 
        print("="*20)
        print("EXIT")
        Cupdate=input("Enter your choice  for updation:")
        allow_column=["product_Name","category","price","Quantity" ,"Payment_Method","Buy_From","Purchase_Date"]
        
        if  Cupdate in allow_column:
            new_value=input("Enter new  value :")
            
            query=f"UPDATE expense set {Cupdate}=%s where Product_Name=%s "
            cursor.execute(query,(new_value,P_name))
            conn.commit()
            print("New value updated successfully !")
            break
        else:
             break
        
        


def delete():
  while True:
        print("\n1. Delete a row ")
        print("\n2. Delete all enteries ")
        print("\n3. Exit")
        Vdelete=int(input("Enter your choice :"))
        if Vdelete==1:
            n=int(input("Enter the SR NO :"))

            query="delete from expense where Product_Name=%s"
            cursor.execute(query,(n,))
            conn.commit()
            print("Row deleted successfully !")
            break
                
        elif Vdelete==2:
            query="truncate table expense restart identity;"
            cursor.execute(query)
            conn.commit()
            print("All enteries deleted successfully !")
            break
        elif Vdelete==3:
            break
   

def more():
    while True:
        print("\n1.Maximum product price")
        print("\n2.Minimum product price")
        print("\n3.Total spend")
        print("\n4.Average product price")
        print("\n5.Product price by ascending order")
        print("\n6.Product price discending oder")
        print("\n7.Count total expense")
        print("\n8.Category wise total spending")
        print("\n9.Top 5 most expensive purchase")
        print("\n10.Exit")
        chh=int(input("enter your choice :"))
        if chh==1:
            query="select max(price) from expense"
            cursor.execute(query)
            result=cursor.fetchone()
            print("Maximun Price :", result[0])

        elif chh==2:
            query="select min(price) from expense"
            cursor.execute(query)
            result=cursor.fetchone()
            print("Minimum Price :", result[0])
        elif chh==3:
            query="select sum(price * Quantity) from expense"
            cursor.execute(query)
            result=cursor.fetchone()
            print("Total spend :", result[0])
        elif chh==4:
            query="select avg(price) from expense"
            cursor.execute(query)
            result=cursor.fetchone()
            print("Average Price :", result[0])
        elif chh==5:
            query="select * from expense order by price "
            cursor.execute(query)
            rows= cursor.fetchall()
            for row in rows:
                print(row)
            
        elif chh==6:
            query="select * from expense order by price desc "
            cursor.execute(query)
            rows= cursor.fetchall()
            for row in rows:
                print(row)

        elif chh==7:
            query="select count(*) from expense "
            cursor.execute(query)
            result=cursor.fetchone()
            print("Total expenses :", result[0])
        elif chh==8:
            query="select category, sum(price * Quantity) from expense group by Category"
            cursor.execute(query)
            rows= cursor.fetchall()
            for row in rows:
                print("Category: ",row[0], "| Total spend:" ,row[1])
            
            

        elif chh==9:
            query="select * from expense order by price desc  limit 5"
            cursor.execute(query)
            rows= cursor.fetchall()
            for row in rows:
                print(row)

        elif chh==10:
            break
        
while True:
    print("\n==== Enxpense Tracker ====\n")
    print("1. Add Expense")
    print("2. View Expense")
    print("3. Update Expense")
    print("4. Delete Expense")
    print("4. More")
    print("6. Exit")
    choice= int(input("Enter your choice: \n"))
    if choice==1:
        add()
    elif choice==2:
        view()
    elif choice==3:
        update()
    elif choice==4:
        delete()
    elif choice==5:
       more()
    elif choice==6:
        break


