import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import scipy.stats as stats
import math
import io

# Session-based login
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.set_page_config(page_title="Login | Grading System", layout="centered")
    st.title("🔐 Faculty Login")
    st.write("Please enter the access password to continue.")

    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == "faculty123":
            st.session_state.authenticated = True
            st.success("Access granted. Redirecting...")
        else:
            st.error("Incorrect password.")

def main_app():

    # Set page config
    st.set_page_config(page_title="Relative Grading Tool", layout="wide")
    
    # Custom styles
    st.markdown("""
        <style>
        .centered-title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #007169;
        }
        .subheader {
            text-align: center;
            font-size: 20px;
            color: #007169;
        }
        .body {
            background-color: #007169;  /* Light blue background */
            color: #007169;  /* Default text color */
        }
        .side-bar{
            color: #007169;
        }
        </style>
    """, unsafe_allow_html=True)
    
    #st.image("college_logo.png", width=100)
    st.markdown('<div class="centered-title">📊 Relative Grading System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Upload Marks, Compute Grades, and Download Instantly</div>', unsafe_allow_html=True)
    st.markdown("---")
    # Create tabs
    tab1, tab2 = st.tabs(["📋 Grading System", "ℹ️ About Us"])
    
    with tab1:
        # Put your entire grading logic here (starting from file upload)
        # For example:
        uploaded_file = st.file_uploader("📂 Upload Excel File (.xlsx)", type="xlsx")
        # [Continue your existing code inside this block]
    
    with tab2:
        st.markdown("## About Us")
        #st.image("college_logo.png", width=100)
        st.markdown("""
        Welcome to the **Relative Grading System**, a final-year project developed by students of the **Department of Computer Science and Engineering**.
    
        ### 🎯 Objective
        Our aim is to simplify the grading process by:
        - Automatically calculating weighted marks.
        - Assigning relative grades using statistical analysis.
        - Providing downloadable, section-wise results.
        - Offering easy search and visualizations.
    
        ### 👥 Team
        - **Sivamanikanta** – Developer & Data Analyst  
        - Guided by: *[Your Mentor/Professor's Name]*
    
        ### 🏫 Institution
        Department of CSE  
        [Your College/University Name]  
        [Location, Year]
    
        Thank you for using our tool!
        """)
    
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("📂 Instructions")
    st.sidebar.markdown("""
    1. Upload an Excel (.xlsx) file.
    2. Ensure `Final_Total` is present or select columns to calculate it.
    3. Choose course type to compute weighted grades.
    4. Search, analyze, and download results.
    """)
    
    
    
    def conditional_ceil(value):
        return math.ceil(value) if value - int(value) >= 0.5 else value
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
            st.success("✅ File uploaded successfully!")
    
            tab1, tab2, tab3 = st.tabs(["📥 Upload & Configure", "📊 Results & Stats", "⬇️ Downloads"])
    
            with tab1:
                # Course type
                course_type = st.radio("📘 Select Course Type:", ["Theory Only", "Theory + Practical"])
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
                if course_type == "Theory Only":
                    selected_cols = st.multiselect("🧮 Select Theory columns (out of 70):", numeric_cols)
                    if selected_cols:
                        df[selected_cols] = df[selected_cols].applymap(conditional_ceil)
                        df['Final_Total'] = df[selected_cols].sum(axis=1)
                        st.success(f"✅ `Final_Total` calculated using (ceil applied): {', '.join(selected_cols)}")
                        st.dataframe(df[['Final_Total'] + selected_cols])
                        df['Pass/Fail'] = df.apply(
                           lambda row: 'Fail' if any(val < 24 for val in row[selected_cols]) else 'Pass',
                           axis=1
                        )
    
    
                elif course_type == "Theory + Practical":
                    theory_cols = st.multiselect("🧮 Select Theory columns (out of 70):", numeric_cols, key="theory")
                    practical_cols = st.multiselect("🧪 Select Practical columns (out of 100):", numeric_cols, key="practical")
    
                    if theory_cols and practical_cols:
                        df[theory_cols] = df[theory_cols].applymap(conditional_ceil)
                        df[practical_cols] = df[practical_cols].applymap(conditional_ceil)
                        theory_total = df[theory_cols].sum(axis=1)
                        practical_total = df[practical_cols].sum(axis=1)
                        df['Final_Total'] = theory_total * 0.7 + practical_total * 0.3
                        st.success("✅ Final_Total computed for Theory + Practical course (weighted).")
                        st.dataframe(df[['Final_Total'] + theory_cols + practical_cols])
                        df['Pass/Fail'] = df.apply(
                        lambda row: (
                            'Fail' if any(val < 24 for val in row[theory_cols]) or any(val < 50 for val in row[practical_cols])
                            else 'Pass'
                        ),
                        axis=1
                        )
    
    
            with tab2:
                st.info("🔍 Calculating class statistics...")
                mu = df['Final_Total'].mean()
                sigma = df['Final_Total'].std()
    
                col1, col2 = st.columns(2)
                col1.metric("📈 Class Average (μ)", f"{mu:.2f}")
                col2.metric("📉 Standard Deviation (σ)", f"{sigma:.2f}")
    
                # Grade assignment
                def assign_grade(mark):
                    if mu + 1.5 * sigma <= mark :
                        return 'O'
                    elif mu + 1.0 * sigma <= mark and mark < mu + 1.5 * sigma:
                        return 'A+'
                    elif mu + 0.5 * sigma <= mark and mark < mu + 1.0 * sigma :
                        return 'A'
                    elif mu - 0.5 * sigma <= mark and mark < mu + 0.5 * sigma:
                        return 'B+'
                    elif mu - 1.0 * sigma <= mark and mark < mu - 0.5 * sigma:
                        return 'B'
                    elif mu - 1.5 * sigma <= mark and mark < mu - 1.0 * sigma:
                        return 'C'
                    elif 35<= mark and mu - 1.0 * sigma:
                        return 'P'
                    else:
                        return 'F'
    
                df['Grade'] = df['Final_Total'].apply(assign_grade)
                st.success("✅ Grades assigned successfully!")
                
    
                # Color-coded grades
                def highlight_grades(val):
                    colors = {
                        'O': '#a2d5c6', 'A+': '#d7f9f1', 'A': '#f6f9c5',
                        'B+': '#ffeabf', 'B': '#ffdfba', 'C': '#ffb3ba',
                        'P': '#16c60c', 'F': '#ff4d4d'
                    }
                    return f'background-color: {colors.get(val, "white")}'
    
                def highlight_passfail(val):
                 return 'background-color: #ffcccc' if val == 'Fail' else 'background-color: #ccffcc'
                st.dataframe(
                    df.style
                    .applymap(highlight_grades, subset=['Grade'])
                    .applymap(highlight_passfail, subset=['Pass/Fail'])
                )
                
                 #search box
                search_query = st.text_input("🔎 Search by Roll Number, Name, or Grade")
                if search_query:
                    # Convert the entire dataframe to string and check for the search query in any column, including 'Grade'
                    filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False)).any(axis=1)]
                    if not filtered_df.empty:
                        st.success(f"Showing results for: {search_query}")
                        st.dataframe(filtered_df)
                    else:
                        st.warning("No matching student found.")
    
                # Grade distribution
                grade_counts = df['Grade'].value_counts().sort_index()
                fig = px.bar(
                    x=grade_counts.index,
                    y=grade_counts.values,
                    labels={'x': 'Grade', 'y': 'Number of Students'},
                    title='🎓 Grade Distribution',
                    text=grade_counts.values
                )
                fig.update_traces(marker_color='skyblue', textposition='outside')
                st.plotly_chart(fig)
    
                # Bell curve
                x_range = np.linspace(df['Final_Total'].min(), df['Final_Total'].max(), 100)
                pdf = stats.norm.pdf(x_range, mu, sigma)
                hist_values, _ = np.histogram(df['Final_Total'], bins=10)
                pdf_scaled = pdf * max(hist_values) / max(pdf)
    
                fig_bell = px.histogram(df, x='Final_Total', nbins=10, opacity=0.6)
                fig_bell.add_scatter(x=x_range, y=pdf_scaled, mode='lines', name='Normal Curve', line=dict(color='red'))
                fig_bell.update_layout(
                    title="📊 Final_Total Distribution with Bell Curve",
                    xaxis_title="Final_Total Marks",
                    yaxis_title="Number of Students",
                    bargap=0.1
                )
                st.plotly_chart(fig_bell)
    
            with tab3:
                # Section-wise download
                if 'Section' in df.columns:
                    sections = df['Section'].dropna().unique()
                    for section in sections:
                        section_df = df[df['Section'] == section]
                        section_buffer = io.BytesIO()
                        with pd.ExcelWriter(section_buffer, engine='openpyxl') as writer:
                            section_df.to_excel(writer, index=False)
                        section_buffer.seek(0)
                        st.download_button(
                            label=f"⬇️ Download Grades for Section {section}",
                            data=section_buffer,
                            file_name=f"grades_section_{section}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("⚠️ No `Section` column found for section-wise downloads.")
    
                # Download entire file
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                output.seek(0)
    
                st.download_button(
                    label="⬇️ Download Full Graded Excel File",
                    data=output,
                    file_name="graded_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.balloons()
    
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align:center;'>© 2025 - Sivamanikanta | Dept. of CSE | 3rd Year Project</p>", unsafe_allow_html=True)


# Entry point
if not st.session_state.authenticated:
    login()
else:
    main_app()
