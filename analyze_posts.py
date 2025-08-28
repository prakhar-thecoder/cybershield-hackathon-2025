import ai_utils
import pandas as pd
import json
import os

def analyze_posts(hashtag):
    # Construct the filename based on the hashtag
    input_path = f"outputs/{hashtag}_high_reach_posts.csv"
    output_path = f"outputs/{hashtag}_anti_india_posts.csv"
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return
    
    # Read the CSV file
    posts_df = pd.read_csv(input_path)
    analyzed_data = []
    
    # Process each post
    for index, post in posts_df.iterrows():
        try:
            print(f"Analyzing post {index + 1}/{len(posts_df)}")
            analysis = ai_utils.analyze_text(post['caption'])
            print(f"Analysis result: {analysis}")
            if analysis["is_anti_india"]:
                post_dict = post.to_dict()
                # Add the three analysis fields directly
                post_dict['is_anti_india'] = analysis['is_anti_india']
                post_dict['threat_score'] = analysis['threat_score']
                post_dict['justification'] = analysis['justification']
                analyzed_data.append(post_dict)
        except Exception as e:
            print(f"Could not analyze post {index}. Error: {e}")
    
    if analyzed_data:
        # Convert the list of dictionaries back to a DataFrame
        analyzed_df = pd.DataFrame(analyzed_data)
        # Save to CSV
        analyzed_df.to_csv(output_path, index=False)
        print(f"Analysis complete. Found {len(analyzed_data)} anti-India posts.")
        print(f"Results saved to {output_path}")
    else:
        print("No anti-India posts found.")

if __name__ == "__main__":
    hashtag = "kashmirbanegapakistan"  # Example hashtag
    analyzed_posts = analyze_posts(hashtag)