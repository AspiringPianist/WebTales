import websockets
import streamlit as st
from api import *

async def display_terminal_output(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            output = await websocket.recv()
            st.text(output)

st.title("Visual Novel Scene Prompt Generator")

# Streamlit interface for the prompt input
st.header("Enter Prompts for Each Scene")
num_scenes = st.number_input("How many scenes?", min_value=1, max_value=100, value=2, step=1)
prompts = []

for i in range(num_scenes):
    prompt = st.text_area(f"Prompt for Scene {i+1}", key=f"prompt_{i}")
    prompts.append(prompt)

# Save the prompts to a file
if st.button("Save Prompts"):
    with open('prompts.txt', 'w') as f:
        for prompt in prompts:
            f.write(prompt.replace('\n', ' ') + "\n")
    st.success("Prompts saved successfully!")

# Button to generate visual novel scenes and open index.html
if st.button("Generate Visual Novel Scenes"):
    with open('prompts.txt', 'r') as f:
        prompts = [line.strip() for line in f.readlines()]
    generate_visual_novel(prompts)
    print("Visual novel generated successfully!")
    st.success("Visual novel generated! Click the button below to open it in a new tab.")
    
if st.button("Open Visual Novel"):
  st.write("""
  <script>
    window.open("index.html", "_blank");
  </script>
""", unsafe_allow_html=True)
st.success("Click the button above to open the visual novel in a new tab.")

