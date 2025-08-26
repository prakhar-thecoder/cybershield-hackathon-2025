import asyncio
import math
import argparse
import analyze_posts
import collect_posts
import filter_high_reach_posts
import prepare_insights
import report_utils


def parse_arguments():
    parser = argparse.ArgumentParser(description='Social media analysis workflow')
    parser.add_argument('--hashtag', type=str, default="kashmirbanegapakistan",
                      help='Hashtag to analyze (default: hashtag)')
    parser.add_argument('--posts', type=int, default=100,
                      help='Number of posts to fetch (default: 100)')
    parser.add_argument('--likes-threshold', type=int, default=50,
                      help='Minimum likes threshold for high-reach posts (default: 50)')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    hashtag = args.hashtag
    posts = args.posts
    likes_threshold = args.likes_threshold
    
    collect_posts.fetch_posts(hashtag, math.ceil(posts / 20))
    filter_high_reach_posts.filter_high_reach_posts(hashtag, likes_threshold)
    analyze_posts.analyze_posts(hashtag)
    top_users_posts = prepare_insights.get_usernames_by_posts(hashtag)
    top_users_reach = prepare_insights.get_usernames_by_reach(hashtag)

    print("Top users by number of posts:", top_users_posts[:5])
    print("Top users by reach:", top_users_reach[:5])

    report_location = asyncio.run(report_utils.prepare_report_async(hashtag))
    print(f"Report generated: {report_location}")