import json
import os
import streamlit as st
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="PlanSync AI - Smart Timetable Generator",
    page_icon="📅",
    layout="wide",
)

# Sidebar for API Key & Settings
st.sidebar.header("⚙️ Configuration")
api_key_input = st.sidebar.text_input(
    "Enter Gemini API Key",
    type="password",
    value=os.environ.get("GEMINI_API_KEY", ""),
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Problem ID C20:** Timetable & Study Plan Generator[cite: 12]"
)
st.sidebar.markdown("**Course:** Prompt Engineering (Bennett University)")

# Main App Header
st.title("📅 PlanSync AI: Intelligent Timetable & Study Plan Generator")
st.markdown(
    "Transform your subjects, syllabus topics, and exam dates into an optimized, constraint-compliant daily study schedule using Gemini and structured outputs."
)

with st.form("study_form"):
  col1, col2 = st.columns(2)
  with col1:
    student_name = st.text_input("Student Name", "Ritik Kumar")
    subjects = st.text_area(
        "Subjects & Topics",
        "Data Structures (Graphs, DP), Algorithms (Sorting, Greedy), Operating"
        " Systems (Processes, Threads)",
    )
  with col2:
    exam_dates = st.text_input(
        "Exam Dates / Timeline", "Maths: Nov 15, OS: Nov 20"
    )
    daily_hours = st.slider(
        "Available Study Hours Per Day", min_value=1, max_value=10, value=4
    )

  submitted = st.form_submit_button(
      "🚀 Generate Constraint-Compliant Timetable"
  )

if submitted:
  if not api_key_input:
    st.error("Please enter your Google Gemini API Key in the sidebar.")
  else:
    try:
      client = genai.Client(api_key=api_key_input)

      system_instruction = (
          "You are PlanSync AI, an expert academic counselor and automated"
          " scheduling engine. Generate a constraint-compliant, balanced,"
          " day-wise study timetable for students[cite: 12]. NO TIME OVERLAPS."
          " Alternate between heavy technical subjects and review sessions."
          " Adhere strictly to the requested JSON schema."
      )

      prompt = f"""
            Student Name: {student_name}
            Subjects & Topics: {subjects}
            Exam Timeline: {exam_dates}
            Available Daily Hours: {daily_hours} hours/day
            
            Generate a 3-day structured study schedule adhering strictly to the JSON schema.
            """

      with st.spinner(
          "🧠 PlanSync AI is computing optimal study slots & checking"
          " constraints..."
      ):
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

      plan_data = json.loads(response.text)

      st.success("✅ Study Plan Generated Successfully!")

      # Render Tabular Timetable for Each Day
      st.markdown("### 📋 Daily Schedule Breakdown & Tables")

      # Handle flexible key names returned by LLM (schedule vs daily_schedule)
      schedule_list = plan_data.get("schedule", []) or plan_data.get(
          "daily_schedule", []
      )

      for day_item in schedule_list:
        day_num = day_item.get("day_number") or day_item.get("day", 1)
        day_focus = day_item.get("focus") or day_item.get("date", "Study Day")

        with st.expander(
            f"📅 Day {day_num}: {day_focus}", expanded=True
        ):
          sessions = day_item.get("sessions") or day_item.get("slots", [])

          # Format data neatly for a table
          table_data = []
          for s in sessions:
            table_data.append({
                "Time Slot": f"{s.get('start_time')} - {s.get('end_time')}",
                "Subject": s.get("subject"),
                "Topic": s.get("topic"),
                "Type": s.get("session_type") or s.get("activity_type"),
                "Objective / Details": s.get("objective")
                or s.get("description", ""),
            })

          if table_data:
            st.table(table_data)
          else:
            st.info("No sessions found for this day.")

    except Exception as e:
      st.error(f"An error occurred during generation: {e}")