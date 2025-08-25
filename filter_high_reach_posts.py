import json

def filter_high_reach_posts(input_path, output_path, like_threshold=50):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_path}.")
        return

    high_reach_posts = [post for post in posts if post.get('like_count', 0) > like_threshold]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(high_reach_posts, f, indent=4)

    print(f"Filtered {len(high_reach_posts)}/{len(posts)} high-reach posts and saved them to {output_path}.")

if __name__ == '__main__':
    filter_high_reach_posts('all_posts.json', 'high_reach_posts.json')