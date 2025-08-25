import pandas as pd
import os

def get_usernames_by_posts(hashtag):
    input_path = f"outputs/{hashtag}_anti_india_posts.csv"
    output_path = f"outputs/{hashtag}_user_post_counts.csv"
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return []
    
    # Read the CSV file
    posts_df = pd.read_csv(input_path)
    
    # Count posts by username and sort in descending order
    user_post_counts = posts_df['username'].value_counts()
    
    # Convert to DataFrame and save to CSV
    user_post_counts_df = user_post_counts.reset_index()
    user_post_counts_df.columns = ['username', 'post_count']
    user_post_counts_df.to_csv(output_path, index=False)
    
    # Convert to list of tuples (username, count)
    return [(username, count) for username, count in user_post_counts.items()]

def get_usernames_by_reach(hashtag):
    input_path = f"outputs/{hashtag}_anti_india_posts.csv"
    output_path = f"outputs/{hashtag}_user_reach.csv"
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return []
    
    # Read the CSV file
    posts_df = pd.read_csv(input_path)
    
    # Calculate total reach for each post (likes + comments)
    posts_df['total_reach'] = posts_df['like_count'] + posts_df['comment_count']
    
    # Group by username and sum the total reach
    user_reach = posts_df.groupby('username')['total_reach'].sum().sort_values(ascending=False)
    
    # Convert to DataFrame and save to CSV
    user_reach_df = user_reach.reset_index()
    user_reach_df.columns = ['username', 'total_reach']
    user_reach_df.to_csv(output_path, index=False)
    
    # Convert to list of tuples (username, total_reach)
    return [(username, int(reach)) for username, reach in user_reach.items()]

if __name__ == "__main__":
    hashtag = "kashmirbanegapakistan"  # Example hashtag
    
    # Get and print top users by post count
    print("\nTop users by post count:")
    top_posters = get_usernames_by_posts(hashtag)
    for username, count in top_posters[:10]:  # Show top 10
        print(f"{username}: {count} posts")
    
    # Get and print top users by reach
    print("\nTop users by total reach:")
    top_reach = get_usernames_by_reach(hashtag)
    for username, reach in top_reach[:10]:  # Show top 10
        print(f"{username}: {reach} total reach")
