import streamlit as st

st.title("Hello, Streamlit!")
st.write("This is my first Streamlit app 🎈")

# Interactive widgets
name = st.text_input("What's your name?")
if name:
    st.write(f"Hello, {name}! 👋")

# Slider example
age = st.slider("Select your age", 0, 100, 25)
st.write("Your age is:", age)
