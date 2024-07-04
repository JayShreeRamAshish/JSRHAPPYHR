import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String,MetaData,inspect
from models import Session, User, Setting, SalaryHeadUpload,engine,Chart,metadata
from passlib.hash import bcrypt
from PIL import Image
from dashboardview import dashboardviews
from udf_report import udfdata
from recruitment import recruitment_view
from PWSalary_View import salary_distribution
from PW_Default import default_dashboard
from sql_dataview import sql_dataview
import base64
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from sql_playground import sql_playground
import logging
from sqlalchemy.exc import SQLAlchemyError
from io import BytesIO
import plotly.express as px
import pickle

st.set_page_config(page_title="Power-VIew HRMS Data Analytics", page_icon=":bar_chart:", layout="wide")

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("styles.css")

# Function to create table
def create_table(table_name, columns):
    table = Table(table_name, metadata, *columns)
    metadata.create_all(bind=engine)
    return table

def udfdata():
    menu = st.selectbox("Action", ["Create Table", "Import Data", "Export Data in Excel"])

    if menu == "Create Table":
        st.header("Create a New Table")
    
        table_name = st.text_input("Table Name")
        number_of_columns = st.number_input("Number of Columns", min_value=1, step=1)

        columns = []
        for i in range(int(number_of_columns)):
            column_name = st.text_input(f"Column {i+1} Name")
            column_type = st.selectbox(f"Column {i+1} Type", ["String", "Integer"], key=f"type_{i}")
            nullable = st.checkbox(f"Column {i+1} Nullable", key=f"nullable_{i}")
            primary_key = st.checkbox(f"Column {i+1} Primary Key", key=f"primary_key_{i}")
            # Default assignment
            col = None
            
            if column_type == "String":
                col = Column(column_name, String, nullable=nullable, primary_key=primary_key)
            elif column_type == "Integer":
                col = Column(column_name, Integer, nullable=nullable, primary_key=primary_key)

            columns.append(col)
    
        if st.button("Create Table"):
            if table_name and columns:
                table = create_table(table_name, columns)
                st.success(f"Table {table_name} created successfully.")
            else:
                st.error("Please enter all required details.")

    elif menu == "Import Data":
        st.header("Import Data to a Table")
    
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        table_name = st.selectbox("Select Table", table_names)
    
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file and table_name:
            data = pd.read_csv(uploaded_file)
            data.to_sql(table_name, con=engine, if_exists='append', index=False)
            st.success(f"Data imported successfully to {table_name}.")

    elif menu == "Export Data in Excel":
        st.header("Export Data to Excel")
    
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        table_name = st.selectbox("Select Table", table_names)
    
        if st.button("Export"):
            query = f"SELECT * FROM {table_name}"
            data = pd.read_sql(query, con=engine)
            data.to_excel(f"{table_name}.xlsx", index=False)
            st.success(f"Data exported successfully to {table_name}.xlsx")
            
# Utility functions
def add_user(username, password):
    session = SessionLocal()
    hashed_password = bcrypt.hash(password)
    new_user = User(username=username, password=hashed_password)
    session.add(new_user)
    session.commit()
    session.close()

def get_user(username):
    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    return user

def verify_password(stored_password, provided_password):
    return bcrypt.verify(provided_password, stored_password)

def update_settings(company_name, logo, slides):
    session = SessionLocal()
    session.query(Setting).delete()
    new_setting = Setting(company_name=company_name, logo=logo, slides=slides)
    session.add(new_setting)
    session.commit()
    session.close()

def get_settings():
    session = SessionLocal()
    settings = session.query(Setting).first()
    session.close()
    return settings

def set_background():
    settings = get_settings()
    if settings and settings.slides:
        img_bytes = settings.slides
        page_bg_img = f'''
        <style>
        body {{
        background-image: url("data:image/png;base64, {base64.b64encode(img_bytes).decode()}");
        background-size: cover;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)



# Super User Login
def login():
    st.sidebar.subheader("Power View",divider=True)
    st.image('powerview.png')
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "Super" and password == "JayShreeRam":
            st.session_state.logged_in = True
            st.rerun()
        else:
            user = get_user(username)
            if user and verify_password(user.password, password):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Incorrect username or password")

# Admin User Management
def admin_management():
    st.subheader("Create Admin User")
    new_username = st.text_input("New Admin Username")
    new_password = st.text_input("New Admin Password", type="password")
    if st.button("Create Admin User"):
        add_user(new_username, new_password)
        st.success("Admin user created successfully!")

# Settings Management
def settings_management():
    st.title("Settings Management")
    st.subheader("Company Info")
    company_name = st.text_input("Company Name")
    logo = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])
    slides = st.file_uploader("Upload Slide Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if st.button("Save Settings"):
        logo_bytes = logo.read() if logo else None
        slides_bytes = [slide.read() for slide in slides] if slides else None
        slides_bytes = b''.join(slides_bytes) if slides_bytes else None
        update_settings(company_name, logo_bytes, slides_bytes)
        st.success("Settings saved successfully!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit app
def Upload_Salary_Head_Data():
    st.title("Upload Salary Head Data")
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)

            # Convert date columns to datetime objects
            date_columns = ['Date of Birth', 'Date of Joining', 'Date of Confirmation', 'Date of Exit']
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

            # Replace NaN values in integer columns with 0
            integer_columns = [
                'Total Days', 'Paid Days', 'OT Hours', 'Gross Basic', 'Gross HRA', 
                'Gross Conveyance', 'Gross Medical', 'Gross Others', 'Gross Special',
                'gross_other1', 'gross_other2', 'gross_other3', 'gross_other4', 'gross_other5',
                'Basic Salary', 'HRA', 'Conveyance Allowance', 'Medical Allowance', 'Other Allowance',
                'Special Allowance', 'other1', 'other2', 'other3', 'other4', 'other5',
                'Incentive', 'Overtime', 'Other Earning', 'Performance Bonus', 'othervar1', 
                'othervar2', 'othervar3', 'othervar4', 'othervar5', 'Income Tax', 'Provident Fund',
                'P Tax', 'ESIC', 'LWF', 'Company Load', 'Salary Advance', 'otherded1', 'otherded2',
                'otherded3', 'otherded4', 'otherded5', 'EPF Employer', 'EPS Employer', 'ESIC Employer',
                'CTC', 'Gross Salary', 'Total Deduction', 'Net Payment'
            ]
            for col in integer_columns:
                df[col] = df[col].fillna(0).astype(float)

            # Replace NaN values in string columns with empty string
            string_columns = [
                'MonthName', 'Employee Code', 'Employee Name', 'Current Month Joined', 'Current Month Exit',
                'Branch', 'Department', 'Designation', 'Grade', 'Project', 'Employee Category', 'Division',
                'Budget Head', 'Bank Name', 'Bank Account number', 'Bank Branch', 'IFSC Code', 
                'PF Applicable', 'Pension Applicable', 'PTAX Applicable', 'ESIC Applicable', 'LWF Applicable',
                'Payment Type'
            ]
            for col in string_columns:
                df[col] = df[col].fillna('')

            st.write("Data Preview:")
            st.write(df)
            if st.button("Upload to Database"):
                try:
                    for index, row in df.iterrows():
                        try:
                            salary_head = SalaryHeadUpload(
                                monthname=row['MonthName'],
                                empcode=row['Employee Code'],
                                empname=row['Employee Name'],
                                empgender=row['Gender'],                                
                                dob=row['Date of Birth'] if pd.notna(row['Date of Birth']) else None,
                                doj=row['Date of Joining'] if pd.notna(row['Date of Joining']) else None,
                                doc=row['Date of Confirmation'] if pd.notna(row['Date of Confirmation']) else None,
                                doe=row['Date of Exit'] if pd.notna(row['Date of Exit']) else None,
                                jicm=row['Current Month Joined'],
                                eicm=row['Current Month Exit'],
                                branch=row['Branch'],
                                department=row['Department'],
                                designation=row['Designation'],
                                grade=row['Grade'],
                                project=row['Project'],
                                empcategory=row['Employee Category'],
                                division=row['Division'],
                                budgethead=row['Budget Head'],
                                bankname=row['Bank Name'],
                                accountnumber=row['Bank Account number'],
                                bankbranch=row['Bank Branch'],
                                ifsccode=row['IFSC Code'],
                                pfapplicable=row['PF Applicable'],
                                pensionapplicable=row['Pension Applicable'],
                                ptapplicable=row['PTAX Applicable'],
                                esicapplicable=row['ESIC Applicable'],
                                lwfapplicable=row['LWF Applicable'],
                                totaldays=row['Total Days'],
                                paiddays=row['Paid Days'],
                                salrytypes=row['Payment Type'],
                                othours=row['OT Hours'],
                                gross_basic=row['Gross Basic'],
                                gross_hra=row['Gross HRA'],
                                gross_conveyance=row['Gross Conveyance'],
                                gross_medical=row['Gross Medical'],
                                gross_other=row['Gross Others'],
                                gross_special=row['Gross Special'],
                                gross_other1=row['gross_other1'],
                                gross_other2=row['gross_other2'],
                                gross_other3=row['gross_other3'],
                                gross_other4=row['gross_other4'],
                                gross_other5=row['gross_other5'],
                                basicsalry=row['Basic Salary'],
                                hra=row['HRA'],
                                conveyance=row['Conveyance Allowance'],
                                medical=row['Medical Allowance'],
                                other=row['Other Allowance'],
                                special=row['Special Allowance'],
                                other1=row['other1'],
                                other2=row['other2'],
                                other3=row['other3'],
                                other4=row['other4'],
                                other5=row['other5'],
                                incentive=row['Incentive'],
                                overtime=row['Overtime'],
                                othereaning=row['Other Earning'],
                                performancebonus=row['Performance Bonus'],
                                othervar1=row['othervar1'],
                                othervar2=row['othervar2'],
                                othervar3=row['othervar3'],
                                othervar4=row['othervar4'],
                                othervar5=row['othervar5'],
                                incometax=row['Income Tax'],
                                providentfund=row['Provident Fund'],
                                ptax=row['P Tax'],
                                esic=row['ESIC'],
                                lwf=row['LWF'],
                                loan=row['Company Load'],
                                advance=row['Salary Advance'],
                                otherded1=row['otherded1'],
                                otherded2=row['otherded2'],
                                otherded3=row['otherded3'],
                                otherded4=row['otherded4'],
                                otherded5=row['otherded5'],
                                epfempr=row['EPF Employer'],
                                epsempr=row['EPS Employer'],
                                esicempr=row['ESIC Employer'],
                                otherempr=row['CTC'],
                                grosssalary=row['Gross Salary'],
                                totaldeduction=row['Total Deduction'],
                                netpay=row['Net Payment']
                            )
                            session.add(salary_head)
                        except Exception as e:
                            logger.error(f"Error adding record at index {index}: {e}")
                            st.error(f"Error adding record at index {index}: {e}")
                    session.commit()
                    st.success("Data uploaded successfully!")
                except SQLAlchemyError as e:
                    logger.error(f"Error during commit: {e}")
                    st.error(f"Error during commit: {e}")
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}")
            st.error(f"Error processing uploaded file: {e}")

# Define column headers
COLUMN_HEADERS = [
    'MonthName', 'Employee Code', 'Employee Name', 'Date of Birth', 'Date of Joining', 'Date of Confirmation',
    'Date of Exit', 'Current Month Joined', 'Current Month Exit', 'Branch', 'Department', 'Designation', 'Grade',
    'Project', 'Employee Category', 'Division', 'Budget Head', 'Bank Name', 'Bank Account number', 'Bank Branch',
    'IFSC Code', 'PF Applicable', 'Pension Applicable', 'PTAX Applicable', 'ESIC Applicable', 'LWF Applicable',
    'Total Days', 'Paid Days', 'Payment Type', 'OT Hours', 'Gross Basic', 'Gross HRA', 'Gross Conveyance',
    'Gross Medical', 'Gross Others', 'Gross Special','gross_other1','gross_other2','gross_other3','gross_other4','gross_other5', 'Basic Salary', 'HRA', 'Conveyance Allowance', 'Medical Allowance',
    'Other Allowance', 'Special Allowance','other1','other2','other3','other4','other5','Incentive', 'Overtime','Other Earning','Performance Bonus','othervar1','othervar2','othervar3','othervar4','othervar5', 'Income Tax', 'Provident Fund',
    'P Tax', 'ESIC', 'LWF', 'Company Load', 'Salary Advance','otherded1','otherded2','otherded3','otherded4','otherded5', 'EPF Employer', 'EPS Employer', 'ESIC Employer', 'CTC',
    'Gross Salary', 'Total Deduction', 'Net Payment'
]

# Function to export data to Excel based on selected month
def export_salary_head_data(selected_month):
    try:
        # Query data for selected month and all required columns
        
        query = session.query(
        SalaryHeadUpload.monthname,
        SalaryHeadUpload.empcode,
        SalaryHeadUpload.empname,
        SalaryHeadUpload.dob,
        SalaryHeadUpload.doj,
        SalaryHeadUpload.doc,
        SalaryHeadUpload.doe,
        SalaryHeadUpload.jicm,
        SalaryHeadUpload.eicm,
        SalaryHeadUpload.branch,
        SalaryHeadUpload.department,
        SalaryHeadUpload.designation,
        SalaryHeadUpload.grade,
        SalaryHeadUpload.project,
        SalaryHeadUpload.empcategory,
        SalaryHeadUpload.division,
        SalaryHeadUpload.budgethead,
        SalaryHeadUpload.bankname,
        SalaryHeadUpload.accountnumber,
        SalaryHeadUpload.bankbranch,
        SalaryHeadUpload.ifsccode,
        SalaryHeadUpload.pfapplicable,
        SalaryHeadUpload.pensionapplicable,
        SalaryHeadUpload.ptapplicable,
        SalaryHeadUpload.esicapplicable,
        SalaryHeadUpload.lwfapplicable,
        SalaryHeadUpload.totaldays,
        SalaryHeadUpload.paiddays,
        SalaryHeadUpload.salrytypes,
        SalaryHeadUpload.othours,
        SalaryHeadUpload.gross_basic,
        SalaryHeadUpload.gross_hra,
        SalaryHeadUpload.gross_conveyance,
        SalaryHeadUpload.gross_medical,
        SalaryHeadUpload.gross_other,
        SalaryHeadUpload.gross_special,
        SalaryHeadUpload.gross_other1,
        SalaryHeadUpload.gross_other2,
        SalaryHeadUpload.gross_other3,
        SalaryHeadUpload.gross_other4,
        SalaryHeadUpload.gross_other5,
        SalaryHeadUpload.basicsalry,
        SalaryHeadUpload.hra,
        SalaryHeadUpload.conveyance,
        SalaryHeadUpload.medical,
        SalaryHeadUpload.other,
        SalaryHeadUpload.special,
        SalaryHeadUpload.other1,
        SalaryHeadUpload.other2,
        SalaryHeadUpload.other3,
        SalaryHeadUpload.other4,
        SalaryHeadUpload.other5,
        SalaryHeadUpload.incentive,
        SalaryHeadUpload.overtime,
        SalaryHeadUpload.othereaning,
        SalaryHeadUpload.performancebonus,
        SalaryHeadUpload.othervar1,
        SalaryHeadUpload.othervar2,
        SalaryHeadUpload.othervar3,
        SalaryHeadUpload.othervar4,
        SalaryHeadUpload.othervar5,
        SalaryHeadUpload.incometax,
        SalaryHeadUpload.providentfund,
        SalaryHeadUpload.ptax,
        SalaryHeadUpload.esic,
        SalaryHeadUpload.lwf,
        SalaryHeadUpload.loan,
        SalaryHeadUpload.advance,
        SalaryHeadUpload.otherded1,
        SalaryHeadUpload.otherded2,
        SalaryHeadUpload.otherded3,
        SalaryHeadUpload.otherded4,
        SalaryHeadUpload.otherded5,
        SalaryHeadUpload.epfempr,
        SalaryHeadUpload.epsempr,
        SalaryHeadUpload.esicempr,
        SalaryHeadUpload.otherempr,
        SalaryHeadUpload.grosssalary,
        SalaryHeadUpload.totaldeduction,
        SalaryHeadUpload.netpay
        ).filter(SalaryHeadUpload.monthname == selected_month).all()

        # Convert query result to DataFrame
        df = pd.DataFrame(query, columns=COLUMN_HEADERS)

        # Convert date columns to string for Excel compatibility
        date_columns = ['Date of Birth', 'Date of Joining', 'Date of Confirmation', 'Date of Exit']
        df[date_columns] = df[date_columns].astype(str)
        # Create a BytesIO buffer
        
        buffer = BytesIO()
            # Generate Excel file and save to buffer
        df.to_excel(buffer, index=False, engine='openpyxl')
    
        # Generate Excel file and prepare download link
        excel_bytes = buffer.getvalue()
        
        # Encode Excel bytes to base64
        b64 = base64.b64encode(excel_bytes).decode()  # Convert bytes to string
        
        # Generate download link
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="salary_data_{selected_month}.xlsx">Download Excel File</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success(f"Data for {selected_month} exported successfully!")

    except SQLAlchemyError as e:
        logger.error(f"Error querying database: {e}")
        st.error(f"Error querying database: {e}")
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        st.error(f"Error exporting data: {e}")

def save_chart_to_db(sql_query, chart_type, Chart_Header, x_axis=None, y_axis=None, color=None, names=None, values=None):
    # Convert list to a string if y_axis is a list
    if y_axis is not None and isinstance(y_axis, list):
        y_axis = ','.join(y_axis)
    
    new_chart = Chart(
        sql_query=sql_query, 
        chart_type=chart_type,
        Chart_Header=Chart_Header,
        x_axis=x_axis,
        y_axis=y_axis,
        color=color,    
        names=names,
        values=values
    )
    session.add(new_chart)
    session.commit()


def load_charts_from_db():
    charts = session.query(Chart).all()
    for chart in charts:
        if chart.y_axis:
            chart.y_axis = chart.y_axis.split(',')
    return charts


    
# Dashboard with Advanced Chart Builder
def advanced_chart_builder():
    # User input for SQL query
    st.subheader("Chart Builder",divider=True)
    sql_query = st.text_area("SQL Query", height=200)

    # Execute the query and fetch data
    if st.button("Run Query"):
        if sql_query.strip() == "":
            st.error("SQL query cannot be empty!")
        else:
            try:
                df = pd.read_sql(sql_query, engine)
                st.session_state.df = df
                st.write("Query Results:")
                st.write(df)
            except Exception as e:
                st.error(f"Error executing query: {e}")
                return

    if 'df' in st.session_state:
        df = st.session_state.df

        # User input for chart type
        st.subheader("Select Chart Type")
        chart_type = st.selectbox("Chart Type", ["Line Chart", "Bar Chart","Pie Chart", "Scatter Plot"])
        x_axis = y_axis = color = names = values = None
        
        # User input for chart customization
        if chart_type in ["Line Chart", "Bar Chart", "Scatter Plot"]:
            x_axis = st.selectbox("Select X-Axis", df.columns)
            y_axis_options = df.columns[df.columns != x_axis]
            y_axis = st.multiselect("Select Y-Axis", y_axis_options)
            color = st.selectbox("Select Color", [None] + list(df.columns))
            
        elif chart_type == "Pie Chart":
            names = st.selectbox("Select Names", df.columns)
            values = st.selectbox("Select Values", df.columns)
                 
        # Generate and display the chart
        st.subheader("Generated Chart")
        try:
            if chart_type == "Line Chart":
                fig = px.line(df, x=x_axis, y=y_axis, color=color)
            elif chart_type == "Bar Chart":
                fig = px.bar(df, x=x_axis, y=y_axis, color=color)
            elif chart_type == "Pie Chart":
                fig = px.pie(df, names=names, values=values)
            elif chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_axis, y=y_axis, color=color)

            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Error generating chart: {e}")

            #sql_query
        
                # Save chart to the database
        Chart_Header = st.text_input("Enter Chart Name")
        if st.button("Save Chart to Database"):
            if chart_type and Chart_Header:
                save_chart_to_db(sql_query, chart_type, Chart_Header, x_axis, y_axis, color, names, values)
                st.success("Chart saved successfully!")
            

# Main App
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
    else:
        #st.sidebar.subheader("Power VIew",divider=True)
        with st.sidebar:
            selected = option_menu(
                menu_title="HappyHR",
                options=["Dashboard", "Manage Database", "HR Admin", "Dashboard Builder", "Developer"],
                icons=["house", "database", "clipboard", "bar-chart", "gear", "code-slash"],
                menu_icon="cast",
                default_index=0,
                styles = {
                            "container": {
                                "padding": "10px",
                                #"background-color": "#f7f9fc",
                                "border-radius": "10px",
                                "box-shadow": "0px 4px 3px rgba(0, 0, 0, 0.1)"},
                            "icon": {
                                #"color": "#2e7bcf",
                                "font-size": "25px",
                                "margin-right": "6px"},
                            "nav-link": {
                                "font-size": "16px",
                                "text-align": "left",
                                "margin": "5px 0",
                                "padding": "10px",
                                "border-radius": "5px",
                                "--hover-color": "#dce6f0",
                                "transition": "background-color 0.3s"},
                            "nav-link-selected": {
                                "background-color": "#2e7bcf",
                                "color": "white",
                                "border-radius": "5px",
                                "padding": "10px"}
                        })
        if selected == "Dashboard":
            pw1=st.sidebar.selectbox("Select",["Default View","Employee Distribution","Salary Distribution","Chart Builder"])
            if pw1=="Default View":
                default_dashboard()
            elif pw1=="Employee Distribution":
                dashboardviews()
            elif pw1=="Salary Distribution":
                salary_distribution()
            elif pw1 == "Chart Builder":
                st.subheader("Power View : Chart Builder", divider=True)
                saved_charts = load_charts_from_db()
                if saved_charts:
                    cols = st.columns(4)  # Adjust the number of columns as needed
                    for i, chart in enumerate(saved_charts):
                        col = cols[i % 4]
                        with col:
                            try:
                                # Refresh data from SQL
                                df = pd.read_sql(chart.sql_query, engine)
                                # Regenerate the chart with fresh data
                                if chart.chart_type == "Line Chart":
                                    fig = px.line(df, x=chart.x_axis, y=chart.y_axis, color=chart.color)
                                elif chart.chart_type == "Bar Chart":
                                    fig = px.bar(df, x=chart.x_axis, y=chart.y_axis, color=chart.color)
                                elif chart.chart_type == "Pie Chart":
                                    fig = px.pie(df, names=chart.names, values=chart.values)
                                elif chart.chart_type == "Scatter Plot":
                                    fig = px.scatter(df, x=chart.x_axis, y=chart.y_axis, color=chart.color)
                                #st.write(f"Query: {chart.sql_query}")
                                #st.write(f"Chart {i + 1}: {chart.chart_type}")
                                st.plotly_chart(fig)
                                st.write(f"View: {chart.Chart_Header}")
                            except Exception as e:
                                st.error(f"Error generating chart: {e}")
        elif selected == "Manage Database":
            pw2=st.sidebar.selectbox("Select",["Import Data from Excel","Export Data From Excel"])
            if pw2=="Import Data from Excel":
                Upload_Salary_Head_Data()
            if pw2=="Export Data From Excel":
                st.subheader("Export Salary Head Data",divider=True)
                # Fetch distinct months from the database
                months = session.query(SalaryHeadUpload.monthname.distinct()).all()
                months = [month[0] for month in months]
                selected_month = st.selectbox("Select Month",months)
                if st.button("Export Data"):
                    export_salary_head_data(selected_month)        
        elif selected == "HR Admin":
            pw3=st.sidebar.selectbox("Option",["Recruitment","Training","PMS","Report"])
            if pw3=="Recruitment":
                recruitment_view()
            if pw3=="Report":
                udfdata()
        elif selected == "Dashboard Builder":
            advanced_chart_builder()
        elif selected == "Developer":
            pw6=st.sidebar.selectbox("Select",["User Defined Datatable","Creat User","Settings","SQL Support"])
            if pw6=="User Defined Datatable":
                udfdata()
            elif pw6=="Creat User":
                admin_management()
            elif pw6=="Settings":
                settings_management()
            elif pw6=="SQL Support":
                sop=st.selectbox("Action",["SQL Table","Play Ground"])
                if sop=="SQL Table":
                    sql_dataview()
                elif sop=="Play Ground":
                    sql_playground()
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()
