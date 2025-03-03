from groq import Groq
import streamlit as st
import os
from dotenv import load_dotenv
import requests
import json

# Set the Streamlit page configuration
st.set_page_config(
    page_title="RAG for Web Search", page_icon="🔍", initial_sidebar_state="collapsed"
)

# Load environment variables
load_dotenv()

# Initialize API clients
groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Set the title of the Streamlit app
st.title("RAG for Web Search")

category = ""

# Number of pages to fetch
page = 1

# Get user query
query = st.text_input("")
if query == "":
    st.info("Enter your search query")
    st.stop()

# Check if nachrichten or news is in the query to set the category
if "nachrichten" in query.lower() or "news" in query.lower():
    category = "news"
else:
    category = "general"


# SearXNG JSON API URL
search_api_url = "https://metosearxng.de/search"


# Collect search results
structured_output = []

for i in range(1, page + 1):
    params = {
        "q": query,
        "format": "json",  # Request JSON response
        "pageno": i,
        "categories": category,
        "engines": "google"
    }

    response = requests.get(search_api_url, params=params)

    if response.status_code == 200:
        data = response.json()  # Parse JSON response

        for result in data.get("results", [])[:30]:
            structured_output.append(
                {"Snippet": result.get("content", ""), "Source": result.get("url", "")}
            )
    else:
        print(f"Failed to fetch page {i}. Status code: {response.status_code}")

# Convert structured data to JSON
output_formatted = json.dumps(structured_output, indent=4)

# Define the system prompt
system_prompt = f"""
Generate a detailed and concise response with a maximum of 500 words using only the provided structured snippets: {output_formatted}.
If the user's query is a question, provide a direct answer in the first paragraph based on the structured snippets.
Then, expand with relevant details using clear, well-structured paragraphs with headings and appropriate spacing.
Do not include any commentary, introduction, or conclusion.
Ensure there are no contradictions in the response.
The response should be in the same language as the user's query.
"""

# Define the LLM model
llama = "llama-3.3-70b-versatile"

# Generate response
chat_completion = groq.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ],
    model=llama,
)

# Extract LLM response
llm_response = chat_completion.choices[0].message.content

# Display response
st.markdown(llm_response, unsafe_allow_html=True)

# Display sources in sidebar
for item in structured_output:
    st.sidebar.markdown(
        f"**Snippet**: {item['Snippet']}  \n\n**Source**: [{item['Source']}]({item['Source']})"
    )

st.write(f"**Number of Sources**: {len(structured_output)}")
