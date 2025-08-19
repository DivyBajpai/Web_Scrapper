"""
Web Scraper - Version 1.1.1 (Streamlit)
Author: Divy Bajpai
Description: Scrapes hyperlinks, titles, headings, and text content in a tree format with Streamlit UI.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import streamlit as st

# Track visited URLs
visited = set()

def get_page_details(url):
    """Fetch and return title, headings, and short text content from the given URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; LinkScraperBot/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else "[No Title]"
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]
        h3_tags = [h.get_text(strip=True) for h in soup.find_all("h3")]

        text_content = soup.get_text(separator=" ", strip=True)
        summary = text_content[:500] + ("..." if len(text_content) > 500 else "")

        return {"title": title, "h1": h1_tags, "h2": h2_tags, "h3": h3_tags, "text": summary}

    except requests.exceptions.RequestException as e:
        return {"title": "[Error]", "h1": [], "h2": [], "h3": [], "text": f"✘ Error: {e}"}

def get_hyperlinks_tree(url, depth=0, max_depth=2):
    """Recursively build a tree of hyperlinks and content details."""
    if url in visited or depth > max_depth:
        return []

    visited.add(url)
    details = get_page_details(url)

    node = {
        "url": url,
        "depth": depth,
        "title": details["title"],
        "h1": details["h1"],
        "h2": details["h2"],
        "h3": details["h3"],
        "text": details["text"],
        "children": [],
    }

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            href = link["href"].strip()
            full_url = urljoin(url, href)
            parsed_url = urlparse(full_url)

            if not parsed_url.scheme.startswith("http"):
                continue

            child = get_hyperlinks_tree(full_url, depth + 1, max_depth)
            node["children"].extend(child)

    except requests.exceptions.RequestException:
        pass

    return [node]

def display_tree(nodes):
    """Display hyperlink tree in Streamlit with expanders."""
    for node in nodes:
        with st.expander(f"🌐 {node['url']} | 📌 {node['title']}", expanded=False):
            st.markdown(f"**URL:** {node['url']}")
            st.markdown(f"**Title:** {node['title']}")
            if node["h1"]:
                st.markdown(f"**🔠 H1:** {', '.join(node['h1'])}")
            if node["h2"]:
                st.markdown(f"**🔤 H2:** {', '.join(node['h2'][:3])} {'...' if len(node['h2']) > 3 else ''}")
            if node["h3"]:
                st.markdown(f"**🔡 H3:** {', '.join(node['h3'][:3])} {'...' if len(node['h3']) > 3 else ''}")
            st.markdown(f"**📝 Text Snippet:** {node['text'][:300]}")

            if node["children"]:
                display_tree(node["children"])

# ---------------- Streamlit App ---------------- #

st.set_page_config(page_title="Web Scraper v1.1.1", layout="wide")
st.title("🌐 Web Scraper - Version 1.1.1")
st.write("Scrape website links, titles, headings, and text content in a tree format.")

with st.form("scraper_form"):
    website_url = st.text_input("🔗 Enter Website URL", "https://example.com")
    max_depth = st.slider("📚 Max Depth", 1, 3, 2)
    submitted = st.form_submit_button("🚀 Start Scraping")

if submitted:
    if not website_url.startswith("http"):
        website_url = "http://" + website_url

    st.info(f"Scraping started for **{website_url}** (Depth: {max_depth})")

    visited.clear()
    with st.spinner("🔄 Scraping in progress... please wait!"):
        tree = get_hyperlinks_tree(website_url, max_depth=max_depth)

    st.success("✅ Scraping complete!")

    if tree:
        display_tree(tree)
    else:
        st.warning("⚠️ No links found or failed to scrape.")
