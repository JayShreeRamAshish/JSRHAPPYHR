import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData
from models import engine

# Database session setup
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
metadata = MetaData()

def udfdata():
    menu = st.sidebar.selectbox("Menu", ["Create Table", "Import Data", "Export Data in Excel", "Advanced Chart Builder", "Advanced Report Builder", "Reports"])

    if menu == "Create Table":
        st.header("Create a New Table")

        table_name = st.text_input("Table Name")
        number_of_columns = st.number_input("Number of Columns", min_value=1, step=1)

        columns = []
        for i in range(int(number_of_columns)):
            column_name = st.text_input(f"Column {i+1} Name")
            column_type = st.selectbox(f"Column {i+1} Type", ["String", "Integer"], key=f"type_{i}")
            nullable = st.checkbox(f"Column {i+1} Nullable", key=f"nullable_{i}")

            if column_type == "String":
                columns.append(Column(column_name, String, nullable=nullable))
            elif column_type == "Integer":
                columns.append(Column(column_name, Integer, nullable=nullable))

        if st.button("Create Table"):
            if table_name and columns:
                table = Table(table_name, metadata, *columns)
                metadata.create_all(engine)
                st.success(f"Table {table_name} created successfully.")
            else:
                st.error("Please enter all required details.")

    elif menu == "Import Data":
        st.header("Import Data to a Table")

        table_names = engine.table_names()
        table_name = st.selectbox("Select Table", table_names)

        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file and table_name:
            data = pd.read_csv(uploaded_file)
            data.to_sql(table_name, con=engine, if_exists='append', index=False)
            st.success(f"Data imported successfully to {table_name}.")

    elif menu == "Export Data in Excel":
        st.header("Export Data to Excel")

        table_names = engine.table_names()
        table_name = st.selectbox("Select Table", table_names)

        if st.button("Export"):
            query = f"SELECT * FROM {table_name}"
            data = pd.read_sql(query, con=engine)
            data.to_excel(f"{table_name}.xlsx", index=False)
            st.success(f"Data exported successfully to {table_name}.xlsx")

    elif menu == "Advanced Chart Builder":
        st.title("Advanced Chart Builder")

        # User input for SQL query
        st.subheader("Enter SQL Query")
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
            chart_type = st.selectbox("Chart Type", ["Line Chart", "Bar Chart", "Histogram", "Pie Chart", "Scatter Plot"])

            # User input for chart customization
            if chart_type in ["Line Chart", "Bar Chart", "Scatter Plot"]:
                x_axis = st.selectbox("Select X-Axis", df.columns)
                y_axis_options = df.columns[df.columns != x_axis]
                y_axis = st.selectbox("Select Y-Axis", y_axis_options)
                color = st.selectbox("Select Color", [None] + list(df.columns))
            elif chart_type == "Histogram":
                x_axis = st.selectbox("Select X-Axis", df.columns)
                y_axis = None
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
                elif chart_type == "Histogram":
                    fig = px.histogram(df, x=x_axis, color=color)
                elif chart_type == "Pie Chart":
                    fig = px.pie(df, names=names, values=values)
                elif chart_type == "Scatter Plot":
                    fig = px.scatter(df, x=x_axis, y=y_axis, color=color)

                st.plotly_chart(fig)
            except Exception as e:
                st.error(f"Error generating chart: {e}")

            # Append chart to the list of charts
            if st.button("Save Chart"):
                if 'saved_charts' not in st.session_state:
                    st.session_state.saved_charts = []
                st.session_state.saved_charts.append((sql_query, chart_type, fig))
                st.success("Chart saved successfully!")

    elif menu == "Advanced Report Builder":
        st.title("Advanced Report Builder")

        # User input for SQL query
        st.subheader("Enter SQL Query")
        sql_query = st.text_area("SQL Query", height=200)

        # Execute the query and fetch data
        if st.button("Run Query"):
            if sql_query.strip() == "":
                st.error("SQL query cannot be empty!")
            else:
                try:
                    df = pd.read_sql(sql_query, engine)
                    st.session_state.report_df = df
                    st.write("Query Results:")
                    st.write(df)
                except Exception as e:
                    st.error(f"Error executing query: {e}")
                    return

        if 'report_df' in st.session_state:
            report_df = st.session_state.report_df

            # Allow user to select template and save the report
            template = st.selectbox("Select Report Template", ["Template 1", "Template 2", "Template 3"])

            if st.button("Save Report"):
                if 'saved_reports' not in st.session_state:
                    st.session_state.saved_reports = []

                report_data = {
                    "sql_query": sql_query,
                    "template": template,
                    "data": report_df.to_dict('records')
                }

                # Save report to session state
                st.session_state.saved_reports.append(report_data)

                # Save report to database (example, you can modify as needed)
                report_table = Table('reports', metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('sql_query', String),
                                     Column('template', String),
                                     Column('data', String))
                metadata.create_all(engine)
                insert_query = report_table.insert().values(
                    sql_query=sql_query,
                    template=template,
                    data=str(report_df.to_dict('records'))
                )
                conn = engine.connect()
                conn.execute(insert_query)
                conn.close()

                st.success("Report saved successfully!")

    elif menu == "Reports":
        st.header("Saved Charts and Reports")

        if 'saved_charts' in st.session_state and st.session_state.saved_charts:
            st.subheader("Saved Charts")
            cols = st.columns(2)  # Adjust the number of columns as needed
            for i, (query, chart_type, fig) in enumerate(st.session_state.saved_charts):
                col = cols[i % 2]
                with col:
                    st.write(f"Chart {i + 1}: {chart_type}")
                    st.write(f"SQL Query: {query}")
                    st.plotly_chart(fig)

        if 'saved_reports' in st.session_state and st.session_state.saved_reports:
            st.subheader("Saved Reports")
            for i, report in enumerate(st.session_state.saved_reports):
                st.write(f"Report {i + 1}:")
                st.write(f"SQL Query: {report['sql_query']}")
                st.write(f"Template: {report['template']}")
                st.write(pd.DataFrame(report['data']))

                # Option to download the report as Excel
                if st.button(f"Download Report {i + 1} as Excel"):
                    df = pd.DataFrame(report['data'])
                    df.to_excel(f"report_{i + 1}.xlsx", index=False)
                    st.success(f"Report {i + 1} downloaded successfully as report_{i + 1}.xlsx")
