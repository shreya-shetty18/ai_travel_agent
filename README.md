<p align="center">
  <img src="https://img.shields.io/badge/Voyager-Travel%20Agent-ff4b4b?style=for-the-badge&logo=streamlit" alt="Voyager Logo">
</p>

<h1 align="center">✈️ Voyager: Travel Agent</h1>

<p align="center">
  <a href="https://voyager-travel-agent.streamlit.app/">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" width="200">
  </a>
</p>



**Voyager: Travel Agent** is a production-grade multi-agent system built on the **Agno** framework, designed to automate end-to-end travel orchestration. By leveraging **Gemini 2.5 Flash** for high-concurrency reasoning and **SerpAPI** for real-time web perception, Voyager transforms unstructured travel intent into structured, actionable itineraries.



## 🚀 Key Features

* **Multi-Agent Orchestration:** Utilizes a specialized `Researcher` for live web-scraping and a `Planner` for architectural synthesis.
* **Gemini 2.0 Flash Integration:** Optimized for low-latency reasoning and a massive context window to handle extensive research data in a single pass.
* **Production-Grade UI:** A refined Streamlit interface featuring sidebar credential management, custom CSS-styled result cards, and real-time execution status tracking.
* **Calendar Synchronization:** Automatically parses AI-generated itineraries into a structured `.ics` file for native integration with Google/Apple Calendar.
* **Secure Secrets Management:** Fully compatible with Streamlit’s `st.secrets` for safe, production-ready deployments.



## 🛠️ Technical Stack

* **Orchestration:** [Agno](https://www.agno.com/)
* **LLM:** Google Gemini 2.5 Flash
* **Web Perception:** SerpAPI (Google Search Engine results)
* **Interface:** Streamlit (Custom CSS-themed)



## 🧠 System Architecture

The agent operates through a collaborative reconciliation loop between specialized agents:

Perception Layer (Researcher): Generates optimized search queries based on destination and duration. It scrapes the live web to aggregate the best activities, dining options, and accommodations.

Reasoning Layer (Planner): Synthesizes raw data from the Researcher into a nuanced, balanced, and coherent day-by-day itinerary.

Action Layer (Calendar Engine): A specialized utility layer that uses Regex to identify "Day X" markers and generate a downloadable .ics calendar object.



## 📅 Calendar Sync Feature

After your itinerary is generated:

Click "Add to Calendar (.ics)" located in the center action bar.

Import the downloaded file into your preferred calendar app (Google, Apple, or Outlook).

Note: Each day appears as an "All-Day" event, with the full AI-generated details stored in the event description for seamless offline access on mobile devices.
