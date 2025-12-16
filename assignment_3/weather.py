import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App Title
st.set_page_config(page_title="Sunbeam Weather App")
st.title("🌞 Sunbeam Weather App")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Home"

# -------------------- PAGES --------------------

def show_home_page():
    st.header("🏠 Home")
    st.write("Welcome to Sunbeam Weather App")

    if st.button("Login"):
        st.session_state.page = "login"


def show_login_page():
    st.header("🔐Login")

    username = st.text_input("Username")
    password = st.text_input("Password")

    if st.button("Login"):
        if username and password and username == password:
            st.toast("Login successful ✅")
            st.session_state.page = "weather"
        else:
            st.toast("Invalid credentials ❌")


def weather_page():
    st.header("🌤 Weather Forecaster")

    city = st.text_input("Enter city")

    if city:
        api_key = os.getenv("api_key")

        if not api_key:
            st.error("API key not found. Please set OPENWEATHER_API_KEY.")
            return

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric"
        )

        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            st.error(data.get("message", "Failed to fetch weather"))
            return

        st.subheader(f"Weather in {city.title()}")

        st.metric("🌡 Temperature (°C)", data["main"]["temp"])
        st.metric("💧 Humidity (%)", data["main"]["humidity"])
        st.metric("🌬 Wind Speed (m/s)", data["wind"]["speed"])

    st.divider()

    if st.button("Logout"):
        st.toast("Thanks!!!")
        st.session_state.page = "Home"


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.header("Navigation")

    if st.button("Home",use_container_width=True):
        st.session_state.page = "Home"

    if st.button("Login",use_container_width=True):
        st.session_state.page = "login"


# -------------------- ROUTER --------------------

if st.session_state.page == "Home":
    show_home_page()

elif st.session_state.page == "login":
    show_login_page()

elif st.session_state.page == "weather":
    weather_page()