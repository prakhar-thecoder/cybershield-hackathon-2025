import csv
import os

posts = []
data_dir = 'all_data'
for filename in os.listdir(data_dir):
    if filename.endswith('.csv'):
        with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                posts.append(row)

print(f"Loaded {len(posts)} posts from CSV files.")
usernames = {}
for post in posts:
    username = post.get('username')
    if username:
        usernames[username] = usernames.get(username, 0) + 1

print(f"Found {len(usernames)} unique users.")
print("\nTop 5 users by number of posts:")
sorted_usernames = sorted(usernames.items(), key=lambda x: x[1], reverse=True)
for username, count in sorted_usernames[:5]:
    print(f"{username}: {count} posts")

print("\nHigh Reach Analysis")
high_reach_users = {}
for post in posts:
    username = post.get('username')
    if username:
        try:
            like_count = int(post.get('like_count', 0))
        except (ValueError, TypeError):
            like_count = 0
        try:
            comment_count = int(post.get('comment_count', 0))
        except (ValueError, TypeError):
            comment_count = 0
        reach_score = like_count + comment_count
        high_reach_users[username] = high_reach_users.get(username, 0) + reach_score

print("Top 5 users by reach score:")
sorted_high_reach_users = sorted(high_reach_users.items(), key=lambda x: x[1], reverse=True)
for username, score in sorted_high_reach_users[:5]:
    print(f"{username}: {score} reach score")