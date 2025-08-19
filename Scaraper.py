# Version 1.0.3 - Web Scraper with Firebase Storage
import streamlit as st
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

# ----------------- Firebase Setup -----------------
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")  # Your downloaded service account key
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ----------------- Scraper Function -----------------
def get_page_details(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title and soup.title.string else "[No Title]"
        h1_tags = [h.get_text(strip=True) for h in soup.find_all('h1')]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all('h2')]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]

        return {
            "url": url,
            "title": title,
            "h1_tags": h1_tags,
            "h2_tags": h2_tags,
            "paragraphs": paragraphs
        }
    except Exception as e:
        return {"error": str(e)}

# ----------------- Streamlit UI -----------------
st.title("🌐 Web Scraper with Firebase (v1.0.3)")

website_url = st.text_input("Enter the website URL:")

if st.button("Scrape and Save"):
    if website_url:
        with st.spinner("🔍 Scraping website..."):
            data = get_page_details(website_url)

        if "error" not in data:
            # Save data to Firebase
            db.collection("scraped_data").add(data)

            # Success message
            st.success("✅ Scraping Successful! Data stored in Firebase 🎉")

            # Show scraped data
            st.subheader("📌 Scraped Data:")
            st.json(data)

            # Optional: Display as table
            st.subheader("📊 Structured View:")
            st.write({
                "Title": data["title"],
                "H1 Tags": ", ".join(data["h1_tags"]),
                "H2 Tags": ", ".join(data["h2_tags"]),
                "Paragraphs (first 3)": data["paragraphs"][:3]  # show only first 3 for readability
            })
        else:
            st.error(f"❌ Error: {data['error']}")
    else:
        st.warning("⚠️ Please enter a valid URL.")
