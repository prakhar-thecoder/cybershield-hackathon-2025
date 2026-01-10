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

    # Process posts in parallel
    print(f"Starting parallel analysis of {len(posts_df)} posts...")

    # Ensure captions are strings
    captions = posts_df["caption"].fillna("").astype(str).tolist()

    # Run batch analysis
    try:
        results = ai_utils.analyze_batch(captions, max_workers=10)
    except Exception as e:
        print(f"Batch analysis failed: {e}")
        return

    # Process results
    for index, (post_dict, analysis) in enumerate(
        zip(posts_df.to_dict("records"), results)
    ):
        try:
            print(f"Processed post {index + 1}/{len(posts_df)}")
            if analysis.get("is_anti_india"):
                # Add the three analysis fields directly
                post_dict["is_anti_india"] = analysis["is_anti_india"]
                post_dict["threat_score"] = analysis["threat_score"]
                post_dict["justification"] = analysis["justification"]
                analyzed_data.append(post_dict)
        except Exception as e:
            print(f"Error processing result for post {index}: {e}")

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
