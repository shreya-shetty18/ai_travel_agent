from textwrap import dedent
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.tools.serpapi import SerpApiTools
import streamlit as st
import re
from agno.models.google import Gemini
from icalendar import Calendar, Event
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Travel Agent", page_icon="✈️", layout="wide")

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1f77b4;
        color: white;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    .itinerary-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- UTILITY FUNCTIONS ---
def generate_ics_content(plan_text:str, start_date: datetime = None) -> bytes:
    """
        Generate an ICS calendar file from a travel itinerary text.

        Args:
            plan_text: The travel itinerary text
            start_date: Optional start date for the itinerary (defaults to today)

        Returns:
            bytes: The ICS file content as bytes
    """
    cal = Calendar()
    cal.add('prodid','-//AI Travel Planner//github.com//' )
    cal.add('version', '2.0')

    if start_date is None:
        start_date = datetime.today()

    day_pattern = re.compile(r'Day (\d+)[:\s]+(.*?)(?=Day \d+|$)', re.DOTALL)
    days = day_pattern.findall(plan_text)

    if not days:
        event = Event()
        event.add('summary', "Travel Itinerary")
        event.add('description', plan_text)
        event.add('dtstart', start_date.date())
        event.add('dtend', start_date.date())
        event.add("dtstamp", datetime.now())
        cal.add_component(event)  
    else:
        for day_num, day_content in days:
            day_num = int(day_num)
            current_date = start_date + timedelta(days=day_num - 1)
            event = Event()
            event.add('summary', f"Day {day_num} Itinerary")
            event.add('description', day_content.strip())
            event.add('dtstart', current_date.date())
            event.add('dtend', current_date.date())
            event.add("dtstamp", datetime.now())
            cal.add_component(event)
    return cal.to_ical()


# --- MAIN UI ---
st.title("✈️ AI Travel Agent")
st.markdown("##### Plan your next adventure!!! Just enter your destination and trip duration, and let the AI do the rest.")
st.divider()

gemini_api_key = st.secrets["GEMINI_API_KEY"]
serp_api_key = st.secrets["SERP_API_KEY"]

if not gemini_api_key or not serp_api_key:
    st.warning("Error processing th request at this time.")
else:
    # --- AGENT INITIALIZATION ---
    researcher = Agent(
        name="Researcher",
        role="Searches for travel destinations, activities, and accommodations based on user preferences",
        model=Gemini(id="gemini-2.5-flash", api_key=gemini_api_key),
        description=dedent(
            """\
        You are a world-class travel researcher. Given a travel destination and the number of days the user wants to travel for,
        generate a list of search terms for finding relevant travel activities and accommodations.
        Then search the web for each term, analyze the results, and return the 10 most relevant results.
        """
        ),
        instructions=[
            "Given a travel destination and the number of days the user wants to travel for, first generate a list of 3 search terms related to that destination and the number of days.",
            "For each search term, `search_google` and analyze the results."
            "From the results of all searches, return the 10 most relevant results to the user's preferences.",
            "Remember: the quality of the results is important.",
        ],
        tools=[SerpApiTools(api_key=serp_api_key)],
        add_datetime_to_context=True,
    )
    
    planner = Agent(
        name="Planner",
         role="Generates a draft itinerary based on user preferences and research results",
        model=Gemini(id="gemini-2.5-flash", api_key=gemini_api_key),
        description=dedent(
            """\
        You are a senior travel planner. Given a travel destination, the number of days the user wants to travel for, and a list of research results,
        your goal is to generate a draft itinerary that meets the user's needs and preferences.
        """
        ),
        instructions=[
            "Given a travel destination, the number of days the user wants to travel for, and a list of research results, generate a draft itinerary that includes suggested activities and accommodations.",
            "Ensure the itinerary is well-structured, informative, and engaging.",
            "Ensure you provide a nuanced and balanced itinerary, quoting facts where possible.",
            "Remember: the quality of the itinerary is important.",
            "Focus on clarity, coherence, and overall quality.",
            "Never make up facts or plagiarize. Always provide proper attribution.",
        ],
        add_datetime_to_context=True,
    )

    # --- INPUT SECTION ---
    c1, c2 = st.columns([2, 1])
    with c1:
        destination = st.text_input("📍 Destination", placeholder="e.g. Kyoto, Japan")
    with c2:
        num_days = st.number_input("📅 Days", min_value=1, max_value=30, value=7)

    # --- SESSION STATE ---
    if 'itinerary' not in st.session_state:
        st.session_state.itinerary = None

    # --- ACTIONS ---
    btn_col, dl_col = st.columns([1, 1])
    
    with btn_col:
        generate_btn = st.button("🚀 Generate Itinerary")
    
    if generate_btn:
        with st.status("🤖 Agent at work...", expanded=True) as status:
            st.write("🔍 Searching for top activities and stays...")
            res: RunOutput = researcher.run(f"Research {destination} for {num_days} days", stream=False)
            
            st.write("📝 Designing your personalized schedule...")
            prompt = f"Destination: {destination}\nDuration: {num_days} days\nResearch: {res.content}"
            plan: RunOutput = planner.run(prompt, stream=False)
            
            st.session_state.itinerary = plan.content
            status.update(label="✅ Itinerary Ready!", state="complete", expanded=False)

    # --- OUTPUT DISPLAY ---
    if st.session_state.itinerary:
        st.divider()
        st.subheader(f"🗺️ Your {num_days}-Day Trip to {destination}")
        
        # Display content in a stylized container
        st.markdown(f'<div class="itinerary-card">{st.session_state.itinerary}</div>', unsafe_allow_html=True)
        
        with dl_col:
            ics_data = generate_ics_content(st.session_state.itinerary)
            st.download_button(
                label="📅 Add to Calendar (.ics)",
                data=ics_data,
                file_name=f"{destination}_itinerary.ics",
                mime="text/calendar"
            )