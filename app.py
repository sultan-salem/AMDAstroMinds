import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---- CONFIG ----
SCRAPINGBEE_API_KEY = st.secrets["SCRAPINGBEE_API_KEY"]
HF_API_KEY = st.secrets["HF_API_KEY"]

CSV_FILE = "SB_publications_PMC.csv"  

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# ---- LOAD CSV ----
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f1f0; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .centered-image {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    .centered-image img {
        opacity: 0.2;          /* Make it semi-transparent */
        position: absolute;    /* Position over background */
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: -1;           /* Push behind main content */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# st.title("NASA Bioscience Publications Explorer")
st.markdown(
    """
    <h1 style='
        text-align: center; 
        font-family: "Trebuchet MS", sans-serif; 
        text-decoration: underline; 
        text-underline-offset: 8px; 
        text-decoration-thickness: 3px;
        margin-bottom: 1px;
    '>
        NASA Bioscience Publications Explorer
    </h1>
    """,
    unsafe_allow_html=True
)
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("AMDASTROMIND.png", width=900)
st.markdown("</div>", unsafe_allow_html=True)



df = pd.read_csv(CSV_FILE)

if 'Title' not in df.columns or 'Link' not in df.columns:
    st.error("CSV must have 'Title' and 'Link' columns.")
else:
    # ---- Search by Title ----
    st.subheader("KEYWORD SEARCH")
    keyword = st.text_input("Enter a keyword to search titles:")

    if keyword:
        filtered_df = df[df['Title'].str.contains(keyword, case=False, na=False)]
    else:
        filtered_df = df

    if len(filtered_df) == 0:
        st.info("No titles found.")
    else:
        # Add placeholder option
        options = ["Select a title"] + filtered_df['Title'].tolist()
        selected_title = st.selectbox("Select a publication:", options)

        if selected_title != "Select a title":
            # Get link for selected publication
            link = filtered_df.loc[filtered_df['Title'] == selected_title, 'Link'].values[0]

            # ---- Scrape Abstract ----
            response = requests.get(
                "https://app.scrapingbee.com/api/v1/",
                params={
                    "api_key": SCRAPINGBEE_API_KEY,
                    "url": link,
                    "render_js": "true"
                }
            )
            soup = BeautifulSoup(response.text, "html.parser")
            abstract_section = soup.find("section", class_="abstract")
            abstract_text = abstract_section.text.strip() if abstract_section else "Abstract not found."

           
            # ---- Summarize Abstract with Hugging Face API ----
            if abstract_text != "Abstract not found.":
                # Create placeholder
                status_placeholder = st.empty()

                # Show loading message
                status_placeholder.info("Generating AI summary...")

                # ---- Call Hugging Face API ----
                payload = {"inputs": f"Summarize this abstract into 3–5 bullet points:\n{abstract_text}"}
                hf_response = requests.post(HF_API_URL, headers=headers, json=payload)
                data = hf_response.json()

                # ---- Update placeholder after generation ----
                if isinstance(data, list) and "summary_text" in data[0]:
                    status_placeholder.success("✅ AI summary generated!")  # replaces old message
                    summary_text = data[0]["summary_text"]
                    sentences = summary_text.split(". ")
                    bullet_points = [f"• {s.strip()}." for s in sentences if s]

                    st.subheader("AI Summary (Bullet Points)")
                    for b in bullet_points:
                        st.write(b)
                else:
                    status_placeholder.error(f"Error from Hugging Face API: {data}")

                # st.info("Generating AI summary...")
                # payload = {"inputs": f"Summarize this abstract into 3–5 bullet points:\n{abstract_text}"}
                # hf_response = requests.post(HF_API_URL, headers=headers, json=payload)
                # data = hf_response.json()

                # if isinstance(data, list) and "summary_text" in data[0]:
                #     st.success("✅ AI summary generated!")   # <-- changed here
                #     summary_text = data[0]["summary_text"]
                #     sentences = summary_text.split(". ")
                #     bullet_points = [f"• {s.strip()}." for s in sentences if s]

                #     st.subheader("AI Summary (Bullet Points)")
                #     for b in bullet_points:
                #         st.write(b)
                # else:
                #     st.error(f"Error from Hugging Face API: {data}")

                



                # payload = {"inputs": f"Summarize this abstract into 3–5 bullet points:\n{abstract_text}"}
                # hf_response = requests.post(HF_API_URL, headers=headers, json=payload)
                # data = hf_response.json()

                # if isinstance(data, list) and "summary_text" in data[0]:
                #     summary_text = data[0]["summary_text"]
                #     # Split into bullet points
                #     sentences = summary_text.split(". ")
                #     bullet_points = [f"• {s.strip()}." for s in sentences if s]

                #     st.subheader("AI Summary (Bullet Points)")
                #     for b in bullet_points:
                #         st.write(b)
                # else:
                #     st.error(f"Error from Hugging Face API: {data}")
