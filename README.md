# WebTales

![WebTales Logo](https://github.com/AspiringPianist/WebTales/blob/master/webtales.jpg?raw=true)

*An AI- powered visual novel generator that crafts your prompts into a fully-fledged visual novel with soundtracks, character images, backgroud images and captivating dialogue and narration. All within a matter of a few minutes. Use it to create advertisement, short sketches, japanese style visual novels, anime theories, etc. Your imagination is the limit!* (Video Demos in the presentation pdf)

## How to Run

This project uses Streamlit to create a visual novel. To run it, follow these steps:
As of now, this uses our API Key, we will change the API key , requirement so that you have to use your own together API key. (Paste it in the api.py script)

**1. Prerequisites:**

  - Make sure you have Python 3.6 or later installed on your system. You can check by running `python --version` in your terminal.
  - Install the required libraries by running the following command in your terminal:

    ```bash
    pip install streamlit json pydantic langchain typing together base64 pillow io
    ```

**2. Clone the Repository:**

   Open a terminal or command prompt and navigate to your desired directory. Clone this repository using the following command:

   ```bash
   git clone https://github.com/AspiringPianist/WebTales.git
  ```

**3. Run the Project:**

Navigate to the project directory:

bash
```
cd WebTales
```
Use code with caution.


Start the Streamlit app using the following command:

bash
```
streamlit run start.py
```
Use code with caution.

This will launch the visual novel in your web browser.

**4. Generate and View the Visual Novel:**

Follow the instructions in the Streamlit app to generate your visual novel. Once the generation is complete, the app will display a message informing you.

**5. Open the Visual Novel:**

![VisualNovelExample](https://github.com/AspiringPianist/WebTales/blob/master/nice.png?raw=true)

Important: After generation, you'll need to manually open the generated index.html file to view the visual novel. This file will typically be located in the same directory as your start.py file.

Open a file explorer and navigate to the project directory (repository in our example). Locate the index.html file and double-click it to open it in your web browser. This will display the generated visual novel.

** Requirements/ pip installs:**

bash
```
streamlit json pydantic langchain typing together base64 pillow io
```

