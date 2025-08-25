import request_utils
import pandas as pd
import os

def fetch_posts(hashtag, pages=1):
    all_posts = []
    next_id = ""
    df = pd.DataFrame(all_posts)
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    df.to_csv(f'outputs/{hashtag}_all_posts.csv', index=False)
    for page in range(1, pages + 1):
        print(f"Fetching page {page}/{pages} for #{hashtag}...")
        posts, next_id = request_utils.get_posts(hashtag=hashtag, next_id=next_id)
        if not posts:
            if page == 1:
                print("Could not fetch any posts. This might be due to an invalid or expired session cookie in request_utils.py")
            else:
                print("No more posts found.")
            break
        all_posts.extend(posts)
        df = pd.DataFrame(all_posts)
        df.to_csv(f'outputs/{hashtag}_all_posts.csv', index=False)
        if not next_id:
            print("No more pages to fetch.")
            break

    if not all_posts:
        print("No posts were saved.")
        return []

    try:
        df = pd.DataFrame(all_posts)
        df.to_csv(f'outputs/{hashtag}_all_posts.csv', index=False)
        print(f"Saved {len(all_posts)} posts to all_posts.csv")
    except (IOError, TypeError) as e:
        print(f"Error saving posts to file: {e}")

    return all_posts


if __name__ == "__main__":
    fetch_posts("kashmirbanegapakistan", pages=1)