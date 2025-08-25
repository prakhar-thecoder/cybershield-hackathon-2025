import pandas as pd

def filter_high_reach_posts(hashtag, like_threshold=50):
    input_path = f"outputs/{hashtag}_all_posts.csv"
    output_path = f"outputs/{hashtag}_high_reach_posts.csv"

    try:
        # Read CSV file into a pandas DataFrame
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: The file {input_path} is empty.")
        return
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return

    # Filter posts with high reach
    high_reach_df = df[df['like_count'] > like_threshold]

    # Save filtered data to CSV
    high_reach_df.to_csv(output_path, index=False)

    print(f"Filtered {len(high_reach_df)}/{len(df)} high-reach posts and saved them to {output_path}.")

if __name__ == '__main__':
    filter_high_reach_posts('kashmirbanegapakistan')