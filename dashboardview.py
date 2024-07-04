import streamlit as st
from models import SalaryHeadUpload, session
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import func
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def get_unique_monthnames():
    unique_monthnames = session.query(SalaryHeadUpload.monthname).distinct().all()
    monthnames_list = [month[0] for month in unique_monthnames]
    return monthnames_list

def get_employee_count_by_attribute(attribute, monthname):
    result = session.query(
        func.count(SalaryHeadUpload.empcode).label('Employee_Count'),
        getattr(SalaryHeadUpload, attribute).label(attribute)
    ).filter(SalaryHeadUpload.monthname == monthname).group_by(getattr(SalaryHeadUpload, attribute)).all()
    
    result_list = [{attribute: getattr(row, attribute), 'Employee_Count': row.Employee_Count} for row in result]
    
    return result_list

def plot_chart(data, title, chart_type):
    labels = [item[list(item.keys())[0]] for item in data]
    counts = [item['Employee_Count'] for item in data]
    
    plt.figure(figsize=(10, 10))
    colors = sns.color_palette("Set2", len(labels))

    if chart_type == 'Pie':
        wedges, texts, autotexts = plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
        plt.axis('equal')
        plt.legend(wedges, labels, title="Categories", loc="lower left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=12)
        for text in texts + autotexts:
            text.set_fontsize(12)
    elif chart_type == 'Bar':
        ax = sns.barplot(x=labels, y=counts, palette='Set2')
        plt.ylabel('Employee Count', fontsize=14)
        plt.xticks(rotation=45, fontsize=14)
        plt.yticks(fontsize=14)
        for i, v in enumerate(counts):
            ax.text(i, v + 1, str(v), ha='center', va='bottom', fontsize=12)
    elif chart_type == 'Line':
        ax = sns.lineplot(x=labels, y=counts, marker='o')
        plt.xlabel('Categories', fontsize=14)
        plt.ylabel('Employee Count', fontsize=14)
        plt.xticks(rotation=45, fontsize=14)
        plt.yticks(fontsize=14)
        for x, y in zip(labels, counts):
            ax.text(x, y, f'{y}', ha='center', va='bottom', fontsize=12)
    elif chart_type == '3D':
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        xpos = np.arange(len(labels))
        ypos = np.zeros_like(xpos)
        zpos = np.zeros_like(xpos)
        dx = dy = 0.5
        dz = counts
        colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
        ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colors, zsort='average')
        ax.set_ylabel('Employee Count', fontsize=14)
        ax.set_zlabel('Count', fontsize=14)
        ax.set_xticks(xpos)
        ax.set_xticklabels(labels, rotation=45, fontsize=12)
        plt.title(title, fontsize=16)
    
    plt.tight_layout()
    st.pyplot(plt)

def dashboardviews():
    unique_monthnames = get_unique_monthnames()
    
    st.subheader('Employee Distribution Dashboard', divider=True)
    row1 = st.columns([3, 1, 1])
    with row1[0]:
        selected_month = st.selectbox('Select Month', unique_monthnames)
    with row1[1]:
        st.empty()
    with row1[2]:
        chart_types = st.multiselect('Select Chart Types', ['Pie', 'Bar', 'Line', '3D'])
    
    if selected_month and chart_types:
        attributes = ['department', 'designation', 'grade', 'project', 'empcategory', 'division', 'budgethead']
        
        data = {}
        for attribute in attributes:
            data[attribute] = get_employee_count_by_attribute(attribute, selected_month)
        
        for attribute in attributes:
            st.markdown(f"### {attribute.capitalize()}")
            
            for i in range(0, len(chart_types), 4):
                cols = st.columns(4)
                for col, chart_type in zip(cols, chart_types[i:i+4]):
                    with col:
                        title = f'Employee Count by {attribute.capitalize()} ({chart_type})'
                        plot_chart(data[attribute], title, chart_type)

if __name__ == "__main__":
    dashboardviews()
