import os
import praw
import base64
import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Create a Reddit instance
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode("utf-8")


# Streamlit app
def main():
    st.title("Reddit Comments Scraper")
    url = st.text_input("Enter the Reddit post URL:")
    if st.button("Scrape Comments"):
        submission = reddit.submission(url=url)

        # Extract all comments including the replies
        comments = []
        columns = [
            "body",
            "score",
            "author",
            "created_utc",
            "id",
            "parent_id",
            "is_top_level",
        ]
        with st.spinner("Scraping comments..."):
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                created_utc = datetime.datetime.fromtimestamp(
                    comment.created_utc, datetime.timezone.utc
                )
                is_top_level = int(comment.parent_id == comment.link_id)
                comments.append(
                    (
                        comment.body,
                        comment.score,
                        comment.author,
                        created_utc,
                        comment.id,
                        comment.parent_id,
                        is_top_level,
                    )
                )

            st.success(f"{len(comments)} comments scraped successfully!")

            # Download CSV
            csv = convert_df(df)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="comments.csv",
                mime="text/csv",
            )

            # Create a DataFrame
            df = pd.DataFrame(comments, columns=columns)
            st.table(df.head(10))


if __name__ == "__main__":
    main()
