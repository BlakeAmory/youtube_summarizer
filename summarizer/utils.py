import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus, urlparse, parse_qs, urlencode
from django.conf import settings
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from langchain_groq import ChatGroq
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

def clean_video_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    clean_query = {"v": query_params.get("v", [""])[0]}
    clean_url = f"https://www.youtube.com/watch?{urlencode(clean_query)}"
    return clean_url


def search_videos(query):
    logger.info(f"Searching for videos with query: {query}")
    base_url = "https://www.youtube.com/results?"
    params = {"search_query": quote_plus(query)}
    url = base_url + "&".join(f"{k}={v}" for k, v in params.items())

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    logger.info(f"Accessing URL: {url}")
    driver.get(url)
    driver.implicitly_wait(10)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    video_elements = soup.select("a#video-title")
    logger.info(f"Found {len(video_elements)} video elements")
    logger.info(f"video_elements: {video_elements}")

    videos = []
    for element in video_elements[:5]:  # Get top 5 results
        video_url = urljoin("https://www.youtube.com", element["href"])
        clean_url = clean_video_url(video_url)
        title = element.get("title", "")
        aria_label = element.get("aria-label", "")
        videos.append({"url": clean_url, "title": title, "info": aria_label})

    for video in videos:
        logger.info(f"Video URL: {video['url']}")

    logger.info(f"Returning {len(videos)} videos")
    return videos


def get_video_info(video_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(video_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("meta", {"property": "og:title"})
    description_tag = soup.find("meta", {"property": "og:description"})
    thumbnail_tag = soup.find("meta", {"property": "og:image"})

    if not title_tag or not description_tag or not thumbnail_tag:
        logger.error(f"Missing meta tags for video URL: {video_url}")
        return {
            "title": "Unknown Title",
            "description": "No description available.",
            "thumbnail": "",
            "url": video_url,
        }

    title = title_tag["content"]
    description = description_tag["content"]
    thumbnail = thumbnail_tag["content"]

    return {
        "title": title,
        "description": description,
        "thumbnail": thumbnail,
        "url": video_url,
    }


def generate_summary(text):
    prompt = f"""
    You are a helpful assistant that provides a comprehensive summary of YouTube videos. The summary should include:

    1. A short description (1-2 sentences) labeled as "Short Description:"
    2. Key points or main ideas (3-5 bullet points) labeled as "Key Points:"
    3. A full summary (3-5 paragraphs) labeled as "Full Summary:"

    Ensure that each section is filled out and not left empty. If there is no information available for a section, explicitly state "No information available."

    Text to summarize:
    {text}

    Format the output exactly as follows:
    Short Description: [Your short description here]

    Key Points:
    - [Key point 1]
    - [Key point 2]
    - [Key point 3]
    - [Key point 4]
    - [Key point 5]

    Full Summary: [Your full summary here]
    """

    logger.debug(f"Generating summary with prompt: {prompt}")
    return generate_summary_with_groq(prompt)


def parse_summary(content):
    logger.debug(f"Parsing summary content: {content}")
    lines = content.split("\n")
    summary = {"short_description": "", "key_points": [], "full_summary": ""}

    current_section = None
    for line in lines:
        if line.startswith("Short Description:"):
            current_section = "short_description"
            summary["short_description"] = line.replace("Short Description:", "").strip()
        elif line.startswith("Key Points:"):
            current_section = "key_points"
        elif line.startswith("Full Summary:"):
            current_section = "full_summary"
        elif current_section == "key_points" and line.strip().startswith("-"):
            summary["key_points"].append(line.strip()[1:].strip())
        elif current_section == "full_summary":
            summary["full_summary"] += line + "\n"

    summary["full_summary"] = summary["full_summary"].strip()
    logger.debug(f"Parsed summary: {summary}")
    return summary


def generate_summary_with_groq(prompt):
    chat_model = get_chat_model()
    messages = [{"role": "user", "content": prompt}]
    response = chat_model.invoke(messages)
    logger.debug(f"Groq API response: {response.content}")
    return parse_summary(response.content)


def summarize_search_results(query):
    videos = search_videos(query)
    summaries = []

    for video in videos:
        video_info = get_video_info(video["url"])
        text_to_summarize = (
            f"Title: {video_info['title']}\n\nDescription: {video_info['description']}"
        )
        summary = generate_summary(text_to_summarize)
        logger.debug(f"Short Description: {summary['short_description']}")
        summaries.append({"video": video_info, "summary": summary})

    return summaries

def get_chat_model():
    return ChatGroq(groq_api_key=settings.GROQ_API_KEY, model_name="mixtral-8x7b-32768")
