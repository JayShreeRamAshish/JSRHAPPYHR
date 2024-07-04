import streamlit as st
from sqlalchemy import create_engine,Column,Float, Integer,String,LargeBinary,DateTime,MetaData,Enum,Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime,date
import pickle

# Database setup
DATABASE_URL = "sqlite:///hrms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
metadata = MetaData()  # Create MetaData instance without bind parameter

# Define the Chart class which maps to the 'charts' table
class Chart(Base):
    __tablename__ = 'charts'
    id = Column(Integer, primary_key=True)
    sql_query = Column(String)
    chart_type = Column(String)
    Chart_Header = Column(String)
    x_axis = Column(String)
    y_axis = Column(String)
    color = Column(String)
    names = Column(String)
    values = Column(String)
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String, nullable=True)
    logo = Column(LargeBinary, nullable=True)
    slides = Column(LargeBinary, nullable=True)

class SalaryHeadUpload(Base):
    __tablename__ = 'salary_head_upload'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # AOS columns
    monthname = Column(String, nullable=False)
    empcode = Column(String, nullable=True)
    empname = Column(String, nullable=True)
    empgender=Column(String, nullable=True)
    dob = Column(DateTime, nullable=True)
    doj = Column(DateTime, nullable=True)
    doc = Column(DateTime, nullable=True)
    doe = Column(DateTime, nullable=True)
    jicm = Column(String, nullable=True)
    eicm = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    project = Column(String, nullable=True)
    empcategory = Column(String, nullable=True)
    division = Column(String, nullable=True)
    budgethead = Column(String, nullable=True)
    bankname = Column(String, nullable=True)
    accountnumber = Column(String, nullable=True)
    bankbranch = Column(String, nullable=True)
    ifsccode = Column(String, nullable=True)
    pfapplicable = Column(String, nullable=True)
    pensionapplicable = Column(String, nullable=True)
    ptapplicable = Column(String, nullable=True)
    esicapplicable = Column(String, nullable=True)
    lwfapplicable = Column(String, nullable=True)
    totaldays = Column(Float, nullable=True)
    paiddays = Column(Float, nullable=True)
    salrytypes = Column(String, nullable=True)
    othours = Column(Float, nullable=True)
    # gross columns
    gross_basic = Column(Float, nullable=True)
    gross_hra = Column(Float, nullable=True)
    gross_conveyance = Column(Float, nullable=True)
    gross_medical = Column(Float, nullable=True)
    gross_other = Column(Float, nullable=True)
    gross_special = Column(Float, nullable=True)
    gross_other1 = Column(Float, nullable=True)
    gross_other2 = Column(Float, nullable=True)
    gross_other3 = Column(Float, nullable=True)
    gross_other4 = Column(Float, nullable=True)
    gross_other5 = Column(Float, nullable=True)
    # earnings columns
    basicsalry = Column(Float, nullable=True)
    hra = Column(Float, nullable=True)
    conveyance = Column(Float, nullable=True)
    medical = Column(Float, nullable=True)
    other = Column(Float, nullable=True)
    special = Column(Float, nullable=True)
    other1 = Column(Float, nullable=True)
    other2 = Column(Float, nullable=True)
    other3 = Column(Float, nullable=True)
    other4 = Column(Float, nullable=True)
    other5 = Column(Float, nullable=True)
    incentive = Column(Float, nullable=True)
    overtime = Column(Float, nullable=True)
    othereaning = Column(Float, nullable=True)
    performancebonus = Column(Float, nullable=True)
    othervar1 = Column(Float, nullable=True)
    othervar2 = Column(Float, nullable=True)
    othervar3 = Column(Float, nullable=True)
    othervar4 = Column(Float, nullable=True)
    othervar5 = Column(Float, nullable=True)
    # deductions
    incometax = Column(Float, nullable=True)
    providentfund = Column(Float, nullable=True)
    ptax = Column(Float, nullable=True)
    esic = Column(Float, nullable=True)
    lwf = Column(Float, nullable=True)
    loan = Column(Float, nullable=True)
    advance = Column(Float, nullable=True)
    otherded1 = Column(Float, nullable=True)
    otherded2 = Column(Float, nullable=True)
    otherded3 = Column(Float, nullable=True)
    otherded4 = Column(Float, nullable=True)
    otherded5 = Column(Float, nullable=True)
    epfempr = Column(Float, nullable=True)
    epsempr = Column(Float, nullable=True)
    esicempr = Column(Float, nullable=True)
    otherempr = Column(Float, nullable=True)
    grosssalary = Column(Float, nullable=True)
    totaldeduction = Column(Float, nullable=True)
    netpay = Column(Float, nullable=True)

class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=date.today())
    vacancy_title = Column(String)
    department = Column(String)
    location = Column(String)
    recruiter = Column(String)
    position = Column(Integer)
    deadline = Column(Date)
    status = Column(Enum('Open', 'Closed', name='vacancy_status'))

class RecruiterTimesheet(Base):
    __tablename__ = 'recruiter_timesheets'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=date.today())
    vacancy_title = Column(String)
    source_of_candidate = Column(String)
    candidate_name = Column(String)
    candidate_emailid = Column(String)
    candidate_mobile = Column(String)
    candidate_resume = Column(String)  # Store file path or file name
    status = Column(Enum('Applied', 'Interviewed', 'Offered', 'Rejected', name='candidate_status'))
    next_action = Column(String)
    milestone = Column(String)
    
# Create all tables in the metadata
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()