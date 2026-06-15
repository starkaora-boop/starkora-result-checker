import streamlit as st
from supabase import create_client

# --- PAGE CONFIG ---
st.set_page_config(page_title="PGA Portal", page_icon="🎒", layout="centered")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #2e1a47 !important; }
    h1, h2, h3, p, label, div { color: #ffffff !important; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #7b2cbf !important; color: white !important; border: none; }
    .report-card-header { background-color: #3c2a5c !important; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .stTable { background-color: #3c2a5c !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- GRADING LOGIC ---
def get_grade_and_remark(score):
    if score >= 80: return "A", "Excellent"
    if score >= 70: return "B", "Very Good"
    if score >= 60: return "C", "Good"
    if score >= 50: return "D", "Credit"
    return "F", "Fail"

# --- SUPABASE SETUP ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- APP INTERFACE ---
st.title("Perfect Gift Academy - Result Checker")
student_id = st.text_input("Enter Student ID", placeholder="e.g., PGA-2026-001")
pin = st.text_input("Enter Access PIN", type="password")
academic_year = st.selectbox("Select Academic Session", ["2025/26"])
selected_term = st.selectbox("Select Term", ["First Term", "Second Term", "Third Term"])

if st.button("Check Result"):
    # 1. Fetch student
    query = supabase.table("students").select("*").eq("student_id", student_id).eq("pin", pin).execute()
    
    if len(query.data) > 0:
        student_data = query.data[0]
        st.markdown(f'<div class="report-card-header"><h3>Welcome, {student_data.get("student_name")}</h3><p>Student ID: {student_id}</p></div>', unsafe_allow_html=True)
        st.write("---")
        
        # 2. Fetch scores
        scores_query = supabase.table("results").select("subject, ca_score, exam_score, total_score")\
            .eq("student_id", student_id).eq("session", academic_year).eq("term", selected_term).execute()
        
        if len(scores_query.data) > 0:
            data = scores_query.data
            for row in data:
                grade, remark = get_grade_and_remark(row['total_score'])
                row['Grade'] = grade
                row['Remark'] = remark
            
            st.subheader("📊 Performance Breakdown")
            st.table(data)
            
            totals = [row['total_score'] for row in data]
            avg_score = sum(totals) / len(totals)
            st.metric(label="Term Average", value=f"{avg_score:.1f}%")
            
            # --- PIN CHANGE SECTION ---
            st.write("---")
            with st.expander("🔑 Change your PIN"):
                new_pin = st.text_input("Enter new secure PIN", type="password", key="new_pin_input")
                if st.button("Update PIN"):
                    if len(new_pin) >= 4:
                        try:
                            supabase.table("students").update({"pin": new_pin}).eq("student_id", student_id).execute()
                            st.success("PIN updated successfully!")
                        except Exception:
                            st.error("Error updating PIN.")
                    else:
                        st.warning("PIN must be at least 4 characters.")
        else:
            st.warning("No academic results found for this session/term.")
    else:
        st.error("Invalid Student ID or Access PIN.")