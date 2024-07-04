import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
from models import engine,Vacancy,RecruiterTimesheet,SalaryHeadUpload,User
import os

Session = sessionmaker(bind=engine)
session = Session()

# Streamlit App
def recruitment_view():
    menu = st.selectbox('Menu', ['Publish Vacancy', 'Recruiter Timesheet'])

    if menu == 'Publish Vacancy':
        st.subheader('Publish Vacancy')

        # Vacancy Form
        unique_departments = session.query(SalaryHeadUpload.department).distinct().all()
        departments_list = [dept[0] for dept in unique_departments]
        
        unique_location = session.query(SalaryHeadUpload.branch).distinct().all()
        location_list = [branch[0] for branch in unique_location]
        
        unique_recruiter = session.query(User.username).distinct().all()
        recruiter_list = [dept[0] for dept in unique_recruiter]
        
        vacancy_title = st.text_input('Vacancy Title')
        department = st.selectbox('Department',departments_list)
        location = st.selectbox('Location',location_list)
        recruiter = st.selectbox('Recruiter',recruiter_list)
        position = st.number_input('Position')
        deadline = st.date_input('Deadline')
        status = st.selectbox('Status', ['Open', 'Closed'])

        if st.button('Publish'):
            # Store in Database
            new_vacancy = Vacancy(vacancy_title=vacancy_title, department=department, location=location,
                                  recruiter=recruiter, position=position, deadline=deadline, status=status)
            session.add(new_vacancy)
            session.commit()
            st.success('Vacancy Published Successfully!')

    elif menu == 'Recruiter Timesheet':
        st.subheader('Recruiter Timesheet')

        # Timesheet Form
        vacancy_title = st.selectbox('Vacancy Title', [v[0] for v in session.query(Vacancy.vacancy_title).distinct().all()])
        source_of_candidate = st.selectbox('Source of Candidate', ['LinkedIn', 'Referral', 'Job Portal'])
        candidate_name = st.text_input('Candidate Name')
        candidate_emailid = st.text_input('Candidate Email ID')
        candidate_mobile = st.text_input('Candidate Mobile Number')
        candidate_resume = st.file_uploader('Candidate Resume', type='pdf')
        status = st.selectbox('Status', ['Applied', 'Interviewed', 'Offered', 'Rejected'])
        next_action = st.text_area('Next Action')
        milestone = st.text_area('Milestone')

        if st.button('Update'):
            if candidate_resume is not None:
                resume_path = os.path.join('resumes', candidate_resume.name)
                with open(resume_path, 'wb') as f:
                    f.write(candidate_resume.getbuffer())
            else:
                resume_path = None

            # Store in Database
            new_entry = RecruiterTimesheet(
                vacancy_title=vacancy_title, source_of_candidate=source_of_candidate, candidate_name=candidate_name,
                candidate_emailid=candidate_emailid, candidate_mobile=candidate_mobile, candidate_resume=resume_path,
                status=status, next_action=next_action, milestone=milestone)
            session.add(new_entry)
            session.commit()
            st.success('Timesheet Updated Successfully!')

    # Display Vacancies
    st.subheader('Current Vacancies')
    vacancies = session.query(Vacancy).all()
    for vacancy in vacancies:
        st.write(f"- {vacancy.vacancy_title}, Department: {vacancy.department}, Location: {vacancy.location}")


if __name__ == '__main__':
    recruitment_view()
