import math
import analyze_posts
import collect_posts
import filter_high_reach_posts
import prepare_insights


if __name__ == "__main__":
    hashtag = "kashmirbanegapakistan"
    posts = 100
    likes_threshold = 50
    
    collect_posts.fetch_posts(hashtag, math.ceil(posts / 18))
    filter_high_reach_posts.filter_high_reach_posts(hashtag, likes_threshold)
    analyze_posts.analyze_posts(hashtag)
    top_users_posts = prepare_insights.get_usernames_by_posts(hashtag)
    top_users_reach = prepare_insights.get_usernames_by_reach(hashtag)

    print("Top users by number of posts:", top_users_posts[:5])
    print("Top users by reach:", top_users_reach[:5])