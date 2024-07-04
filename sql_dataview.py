import streamlit as st
from sqlalchemy import create_engine, MetaData, Table
from models import metadata,engine


# Reflect all tables from the database
metadata.reflect(bind=engine)

# Get a list of all table names
table_names = metadata.tables.keys()
def sql_dataview():
    st.subheader("Database Tables and Fields",divider=True)

    # Radio button for table selection
    col1,col2=st.columns(2)
    with col1:
        selected_table = st.radio("Select a table to view details", list(table_names))

        if selected_table:
        # Fetch the table object
            table = Table(selected_table, metadata, autoload_with=engine)

            st.write(f"### Table: {selected_table}")
    with col2:
        # Display the table name and its fields
        st.write("**Fields:**")
        fields = [column.name for column in table.columns]
        st.write(fields)

        # Display detailed information upon selecting a radio button
        expand_details = st.radio("Do you want to see the detailed schema?", ["No", "Yes"])

        if expand_details == "Yes":
            st.write("**Detailed Schema:**")
            for column in table.columns:
                st.write(f"Name: {column.name}, Type: {column.type}")

