import csv
import time
import re
import html
import nltk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from nltk.sentiment import SentimentIntensityAnalyzer
import pymysql
import pandas as pd

# ------------------- MySQL Connection -------------------
conn = pymysql.connect(host="localhost", user="root", password="Gauthu@12", db="e_book")
cursor = conn.cursor()

# ------------------- Download NLTK Resources -------------------
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# ------------------- Cleaning Functions -------------------
def clean_review(review):
    review = re.sub(r'<.*?>', '', review)
    review = html.unescape(review)
    review = review.replace('\n', ' ')
    return review.strip()

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# ------------------- Selenium Setup -------------------
chrome_driver_path = r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
options = Options()
options.add_argument(f"user-agent={user_agent}")
options.add_argument("--disable-blink-features=AutomationControlled")
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

all_reviews = []

# ------------------- Scrape Goodreads -------------------
driver.get("https://www.goodreads.com/book/popular_by_date")
time.sleep(5)

book_cards = driver.find_elements(By.CSS_SELECTOR, "article.BookListItem")[:10]

for idx, card in enumerate(book_cards, start=1):
    try:
        title = card.find_element(By.CSS_SELECTOR, 'a[data-testid="bookTitle"]').text.strip()
        author = card.find_element(By.CSS_SELECTOR, 'span[data-testid="name"]').text.strip()
        book_url = card.find_element(By.CSS_SELECTOR, 'a[data-testid="bookTitle"]').get_attribute("href")
        cover = card.find_element(By.CSS_SELECTOR, 'img.ResponsiveImage').get_attribute("src")
        rating = card.find_element(By.CSS_SELECTOR, '.Text.Text__body3.Text__semibold.Text__body-standard').text.strip()

        print(f"\nBook {idx}: {title}")

        # Open book details in a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(book_url)
        time.sleep(5)

        # Scroll to load reviews
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        review_cards = driver.find_elements(By.CSS_SELECTOR, 'article.ReviewCard')

        for review_card in review_cards:
            try:
                reviewer = review_card.find_element(By.CSS_SELECTOR, '[data-testid="name"] a').text.strip()
                review_html = review_card.find_element(By.CSS_SELECTOR, '[data-testid="contentContainer"] span.Formatted').get_attribute("innerHTML")

                parts = review_html.split("<br>")
                cleaned = [p.strip() for p in parts if p.strip()]
                review_text = "\n".join(cleaned[:2])

                review_text = clean_review(review_text)
                review_text = remove_emojis(review_text)

                sentiment_scores = sia.polarity_scores(review_text)
                pos_score = sentiment_scores['pos']
                neg_score = sentiment_scores['neg']

                contributing_positive = []
                contributing_negative = []

                for word in review_text.split():
                    score = sia.lexicon.get(word.lower())
                    if score:
                        if score > 0:
                            contributing_positive.append(word)
                        elif score < 0:
                            contributing_negative.append(word)

                all_reviews.append({
                    "Book_Title": title,
                    "Author": author,
                    "Rating": rating,
                    "Reviewer": reviewer,
                    "Review_Text": review_text,
                    "Positive_Score": pos_score,
                    "Negative_Score": neg_score,
                    "Positive_Words": ', '.join(contributing_positive),
                    "Negative_Words": ', '.join(contributing_negative),
                    "Book_URL": book_url,
                    "Cover_URL": cover
                })

            except Exception as e:
                print(f"Review error: {e}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"Book error: {e}")

driver.quit()

# ------------------- Save to CSV -------------------
csv_file = "goodreads_reviews_with_sentiment.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    fieldnames = ["Book_Title", "Author", "Rating", "Reviewer", "Review_Text", "Positive_Score", "Negative_Score",
                  "Positive_Words", "Negative_Words", "Book_URL", "Cover_URL"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_reviews)

# ------------------- Load into Database -------------------
books = pd.read_csv(csv_file)

insert_query = """
INSERT INTO new_arrivals 
(title, author, rating, reviewer, review_text, positive_score, negative_score, positive_words, negative_words, book_url, image_url)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for _, row in books.iterrows():
    try:
        cursor.execute(insert_query, (
            row['Book_Title'],
            row['Author'],
            row['Rating'],
            row['Reviewer'],
            row['Review_Text'],
            row['Positive_Score'],
            row['Negative_Score'],
            row['Positive_Words'],
            row['Negative_Words'],
            row['Book_URL'],
            row['Cover_URL']
        ))
    except Exception as e:
        print(f"DB insert error for book '{row['Book_Title']}': {e}")

conn.commit()
conn.close()

print(f"\n Data saved to '{csv_file}' and database successfully updated.")
