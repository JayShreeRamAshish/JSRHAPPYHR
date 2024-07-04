import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import sessionmaker
from models import SalaryHeadUpload, engine

# Set up SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

# Fetch data from the database
@st.cache_resource
def load_data():
    result = session.query(SalaryHeadUpload).all()
    return pd.DataFrame([{
        'monthname': row.monthname,
        'gross_basic': row.gross_basic,
        'gross_hra': row.gross_hra,
        'gross_conveyance': row.gross_conveyance,
        'gross_medical': row.gross_medical,
        'gross_other': row.gross_other,
        'gross_special': row.gross_special,
        'basicsalry': row.basicsalry,
        'hra': row.hra,
        'conveyance': row.conveyance,
        'medical': row.medical,
        'other': row.other,
        'special': row.special,
        'incentive': row.incentive,
        'overtime': row.overtime,
        'othereaning': row.othereaning,
        'performancebonus': row.performancebonus,
        'incometax': row.incometax,
        'providentfund': row.providentfund,
        'ptax': row.ptax,
        'esic': row.esic,
        'lwf': row.lwf,
        'loan': row.loan,
        'advance': row.advance,
        'grosssalary': row.grosssalary,
        'totaldeduction': row.totaldeduction,
        'netpay': row.netpay,
    } for row in result])

def salary_distribution():
    df = load_data()

    # Streamlit app
    st.subheader("Dynamic Salary Distribution", divider=True)
    
    # Multi-select for months and chart types in the same row
    col1, col2 = st.columns([2, 1])

    # Multi-select for months
    with col1:
        months = st.multiselect("Select Month(s)", options=df['monthname'].unique())
    
    # Multi-select for chart types
    with col2:
        chart_types = st.multiselect(
            "Select Chart Type(s)",
            options=['Bar', 'Line', 'Area', 'Pie', 'Scatter']
        )

    # Multi-select for salary heads
    salary_heads = st.multiselect(
        "Select Salary Head(s)",
        options=[
            'gross_basic', 'gross_hra', 'gross_conveyance', 'gross_medical', 'gross_other', 'gross_special',
            'basicsalry', 'hra', 'conveyance', 'medical', 'other', 'special',
            'incentive', 'overtime', 'othereaning', 'performancebonus', 'incometax',
            'providentfund', 'ptax', 'esic', 'lwf', 'loan', 'advance', 'grosssalary',
            'totaldeduction', 'netpay']
    )

    if not months or not salary_heads or not chart_types:
        st.warning("Please select at least one month, one salary head, and one chart type.")
    else:
        # Filter data based on user selection
        filtered_df = df[df['monthname'].isin(months)]

        # Display filtered DataFrame
        st.write("Filtered Data:")
        st.dataframe(filtered_df)

        if filtered_df.empty:
            st.warning("No data available for the selected month(s). Please choose different month(s).")
        else:
            # Group by month and sum the selected salary heads
            grouped_df = filtered_df.groupby('monthname')[salary_heads].sum().reset_index()

            # Melt the dataframe for better plotting
            melted_df = grouped_df.melt(id_vars='monthname', var_name='Salary Head', value_name='Total Salary')

            # Function to create chart based on type
            def create_chart(chart_type):
                if chart_type == 'Bar':
                    return px.bar(melted_df, x='monthname', y='Total Salary', color='Salary Head', barmode='group')
                elif chart_type == 'Line':
                    return px.line(melted_df, x='monthname', y='Total Salary', color='Salary Head', markers=True)
                elif chart_type == 'Area':
                    return px.area(melted_df, x='monthname', y='Total Salary', color='Salary Head', groupnorm='percent')
                elif chart_type == 'Pie':
                    return px.pie(melted_df, names='Salary Head', values='Total Salary', hole=0.3)
                elif chart_type == 'Scatter':
                    return px.scatter(melted_df, x='monthname', y='Total Salary', color='Salary Head', size='Total Salary')

            # Display charts in a single row
            cols = st.columns(len(chart_types))

            for col, chart_type in zip(cols, chart_types):
                fig = create_chart(chart_type)
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Sum of Salary",
                    legend_title="Salary Head",
                    template="plotly_dark",
                    font=dict(
                        family="Arial, sans-serif",
                        size=14,
                        color="white"
                    ),
                    hovermode="x unified",
                    title={
                        'text': f"Salary Head Chart - {chart_type}",
                        'y': 0.9,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )

                # Update tooltip
                fig.update_traces(
                    hovertemplate='<b>Month</b>: %{x}<br><b>Total Salary</b>: %{y}<br><b>Salary Head</b>: %{customdata[0]}<extra></extra>',
                    customdata=melted_df[['Salary Head']]
                )

                col.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    salary_distribution()
