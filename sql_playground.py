import streamlit as st
import pandas as pd
from models import Session
from sqlalchemy import text
import io

def sql_playground():
    st.subheader("SQL Playground")
    session = Session()
    
    query = st.text_area("Write your SQL query here")
    execute = st.button("Execute")

    if execute:
        try:
            result = session.execute(text(query)).fetchall()
            columns = result[0].keys() if result else []
            df = pd.DataFrame(result, columns=columns)
            st.write(df)

            # Export options
            if st.button("Export to Excel"):
                towrite = io.BytesIO()
                df.to_excel(towrite, index=False, engine='xlsxwriter')
                towrite.seek(0)
                st.download_button(
                    label="Download Excel file",
                    data=towrite,
                    file_name="query_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            if st.button("Export to PDF"):
                import pdfkit
                html_string = df.to_html()
                pdf_file_path = 'query_result.pdf'
                pdfkit.from_string(html_string, pdf_file_path)
                with open(pdf_file_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download PDF file",
                        data=pdf_file,
                        file_name="query_result.pdf",
                        mime="application/pdf"
                    )
        except Exception as e:
            st.error(f"An error occurred: {e}")

    session.close()

if __name__ == "__main__":
    sql_playground()
