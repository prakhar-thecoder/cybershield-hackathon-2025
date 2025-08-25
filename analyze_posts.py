import ai_utils
import json

def analyze_posts_in_batches(posts, batch_size=10):
    anti_indian_posts = []
    with open("anti_indian_posts.json", "w") as file:
        json.dump([], file)
    
    for i in range(0, len(posts), batch_size):
        batch = posts[i:i + batch_size]
        print(f"Analyzing batch {i//batch_size + 1}/{(len(posts) + batch_size - 1)//batch_size}")
        
        captions = [post.get("caption", "") for post in batch]
        
        try:
            analyses = ai_utils.analyze_batch(captions)
            for post, analysis in zip(batch, analyses):
                if analysis.is_anti_india:
                    post["analysis"] = analysis.__dict__
                    anti_indian_posts.append(post)
                    with open("anti_indian_posts.json", "w") as file:
                        json.dump(anti_indian_posts, file, indent=4)
        except Exception as e:
            print(f"Could not process batch {i//batch_size + 1}. Error: {e}")

    return anti_indian_posts


if __name__ == "__main__":
    posts = []
    with open("high_reach_posts.json", "r") as file:
        posts = json.load(file)
    
    anti_indian_posts = analyze_posts_in_batches(posts, batch_size=10)
    
    with open("anti_indian_posts.json", "w") as file:
        json.dump(anti_indian_posts, file, indent=4)
    
    print(f"Found {len(anti_indian_posts)} anti-Indian posts.")