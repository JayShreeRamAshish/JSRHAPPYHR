import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey,func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from models import SalaryHeadUpload, engine
import altair as alt
import pandas as pd



# Establish a session with the database
Session = sessionmaker(bind=engine)
session = Session()



# Function to calculate and display attrition rate
def default_views():
    # Fetch month options from the database
    month_options = session.query(SalaryHeadUpload.monthname).distinct().all()
    month_options = [month[0] for month in month_options]
    selected_month = st.multiselect("Select Month", month_options)

    # Chart Type selection
    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart", "Attrition Rate Chart"])


def monthwisesalary():
    # Assuming `SalaryHeadUpload` is already defined as in your provided model
    query = (
    session.query(SalaryHeadUpload.monthname, func.sum(SalaryHeadUpload.grosssalary).label('total_grosssalary'))
    .group_by(SalaryHeadUpload.monthname)
    .order_by(SalaryHeadUpload.monthname)
    ).all()

    # Convert query result to a dictionary
    data = [{'monthname': month, 'total_grosssalary': total} for month, total in query]
    

    # Convert data to a DataFrame
    df = pd.DataFrame(data)

    # Create an Altair chart
    chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('monthname:N', sort='-y', title='Month'),
    y=alt.Y('total_grosssalary:Q', title='Total Gross Salary'),
    tooltip=['monthname', 'total_grosssalary']
    ).properties(
    title='Month-wise Total Gross Salary',
    width=600,
    height=400
    ).configure_axis(
    labelFontSize=12,
    titleFontSize=14
    ).configure_title(
    fontSize=16
    )
    st.altair_chart(chart, use_container_width=True)

def default_dashboard():
    monthwisesalary()
    
# Run the default dashboard function
if __name__ == "__main__":
    default_dashboard()