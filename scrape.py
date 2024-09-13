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

        # Create a DataFrame
        df = pd.DataFrame(comments, columns=columns)
        st.write(df)

        # Download CSV
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="comments.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
