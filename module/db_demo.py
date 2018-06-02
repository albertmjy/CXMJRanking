import os
import sqlite3
from sqlite3 import Error
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.sql import select, asc, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


def create_table(conn):
    conn.execute('''CREATE TABLE COMPANY
             (ID INT PRIMARY KEY     NOT NULL,
             NAME           TEXT    NOT NULL,
             AGE            INT     NOT NULL,
             ADDRESS        CHAR(50),
             SALARY         REAL);''')
    print("table created")

def insert_data(conn):
    conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
              VALUES (1, 'Paul', 32, 'California', 20000.00 )");

    conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
              VALUES (2, 'Allen', 25, 'Texas', 15000.00 )");

    conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
              VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )");

    conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
              VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )");
    conn.commit()

db_file = "databases/todo.db"

def sqlite_test():
    try:
        conn = sqlite3.connect(db_file)
        # cursor = conn.execute("SELECT id, name, address, salary from COMPANY")
        cursor = conn.execute("SELECT * from COMPANY")

        print(cursor.fetchall())

        for row in cursor:
            print(row, row[2])

    except Error as e:
        print(e)
    finally:
        conn.close()

def sqlalchemy_test():
    eng = create_engine("sqlite:///databases/todo.db")
    meta = MetaData(eng)
    meta.reflect(bind=eng)

    for table in meta.tables:
        print(table)


    with eng.connect() as conn:
        company = Table('company', meta, autoload=True)
        print(company.c)

        ins = company.insert().values(ID=6, NAME='Peter', AGE=30, ADDRESS='Shanghai', SALARY=1000)
        conn.execute(ins)

        stmt = select([company]).where(company.c.AGE > 24).order_by(asc(company.c.NAME))
        rs = conn.execute(stmt)
        print(rs.fetchall())
        # rs = conn.execute('SELECT * from COMPANY')
        # data = rs.keys()
        # print("data: ", data)


def sqlalchemy_orm():
    # eng = create_engine('sqlite:///:memory:')
    eng = create_engine('sqlite:///databases/todo.db')
    Base = declarative_base()

    class Car(Base):
        __tablename__ = "Cars"

        Id = Column(Integer, primary_key=True)
        Name = Column(String)
        Price = Column(String)

    Base.metadata.bind = eng
    Base.metadata.create_all()

    Session = sessionmaker(bind=eng)
    ses = Session()

    ses.add_all(
        [Car(Id=1, Name='Audi', Price=52642),
         Car(Id=2, Name='Mercedes', Price=57127),
         Car(Id=3, Name='Skoda', Price=9000),
         Car(Id=4, Name='Volvo', Price=29000),
         Car(Id=5, Name='Bentley', Price=350000),
         Car(Id=6, Name='Citroen', Price=21000),
         Car(Id=7, Name='Hummer', Price=41400),
         Car(Id=8, Name='Volkswagen', Price=21600)])

    c1 = Car(Name='Oldsmobile', Price=23450)
    ses.add(c1)

    ses.commit()

    rs = ses.query(Car).filter(Car.Id.in_([2,3,4,6,8,9]))

    for car in rs:
        print(car.Id, car.Name, car.Price)


def sqlalchemy_orm_2():
    # eng = create_engine('sqlite:///:memory:')
    eng = create_engine('sqlite:///databases/todo.db')

    Base = declarative_base()
    # Base.metadata.bind = eng

    class Car(Base):
        __tablename__ = "Cars"

        Id = Column(Integer, primary_key=True)
        Name = Column(String)
        Price = Column(String)

    Session = sessionmaker(bind=eng)
    ses = Session()

    rs = ses.query(Car).filter(Car.Id.in_([2, 4, 6, 8]))

    for car in rs:
        print(car.Id, car.Name, car.Price)

def sqlalchemy_orm_foreignkey():
    # eng = create_engine('sqlite:///:memory:')
    eng = create_engine('sqlite:///databases/todo.db')
    Base = declarative_base()

    class Author(Base):
        __tablename__ = "Authors"

        AuthorId = Column(Integer, primary_key=True)
        Name = Column(String)
        Books = relationship("Book")

    class Book(Base):
        __tablename__ = "Books"

        BookId = Column(Integer, primary_key=True)
        Title = Column(String)
        AuthorId = Column(Integer, ForeignKey("Authors.AuthorId"))

        Author = relationship("Author")

    Base.metadata.create_all(eng)

    Session = sessionmaker(bind=eng)
    ses = Session()

    ses.commit()

    res = ses.query(Author).filter(Author.Name == "Leo Tolstoy").first()

    for book in res.Books:
        print(book.__dir__())

if __name__ == "__main__":
    sqlalchemy_orm_foreignkey()


db_is_new = not os.path.exists(db_file)
if (db_is_new):
    print("need to create")
else:
    print("exists ")