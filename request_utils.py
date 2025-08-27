import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def get_posts(hashtag, next_id=None):
    base_url = "https://www.instagram.com/api/v1/fbsearch/web/top_serp/"
    
    params = {
        'enable_metadata': 'true',
        'query': f'#{hashtag}',
        'search_session_id': '',
        'rank_token': 'df402e40-c3f8-490f-9625-0ce20d3907e5'
    }

    if next_id:
        params['next_max_id'] = next_id

    # NOTE: The 'Cookie' and other headers below contain authentication tokens that might expire.
    # If you are getting errors, you may need to get new values for these from your browser's developer tools
    # when making a similar request on instagram.com.
    headers = {
        'Host': 'www.instagram.com',
        'Cookie': 'ig_did=91CB9BA0-9D5B-4B65-BFCF-D95ACCFFF6D6; csrftoken=F1X2AGikaWatFfSh85MWHn; datr=QE2paLXCjJTRDiTd4GNckQnw; wd=1481x752; dpr=1.25; mid=aKlNQAAEAAHzxk2_5yJVxVsng6hw; ps_l=1; ps_n=1; ig_nrcb=1; ds_user_id=70280221872; sessionid=70280221872%3AkHwiWSioM3sOab%3A4%3AAYdKl09e1YzFjFHRmyVJh64tsvYCzcoebmD1y8sBsQ; rur="CCO\\05470280221872\\0541787564974:01fe6db3d8d8aee318b0efaff3b92747afcf13bc0ac47ff2f1f01d876f35d0637f08a1fe"',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Csrftoken': 'F1X2AGikaWatFfSh85MWHn',
        'X-Ig-App-Id': '936619743392459',
        'X-Asbd-Id': '359341',
        'X-Ig-Www-Claim': 'hmac.AR0zFGi2tmkqNwb6dxwg-ypoJ98WT8iQc9TRcfOu9JAWXO-Q',
        'X-Web-Session-Id': '3ph857:prfqbd:zt0tki',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'https://www.instagram.com/explore/search/keyword/?q=%23{hashtag}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Te': 'trailers'
    }

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        with open('outputs/raw_response.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        if not isinstance(data, dict):
            print("Error: Response is not a valid JSON object.")
            return [], None

        media_grid = data.get('media_grid', {})
        if not isinstance(media_grid, dict):
            print("Error: 'media_grid' is not a valid JSON object.")
            return [], None
            
        next_max_id = media_grid.get('next_max_id')

        all_posts = []
        sections = media_grid.get('sections', [])
        
        if not isinstance(sections, list):
            print("Error: 'sections' is not a list.")
            return [], None

        for section in sections:
            if not isinstance(section, dict):
                continue
            layout_content = section.get('layout_content', {})
            if not isinstance(layout_content, dict):
                continue
            medias = layout_content.get('medias', [])
            if not isinstance(medias, list):
                continue

            for item in medias:
                try:
                    if not isinstance(item, dict):
                        continue
                    media = item.get('media', {})
                    if not media or not isinstance(media, dict):
                        continue

                    username = media.get('user', {}).get('username')
                    user_url = f"https://www.instagram.com/{username}/" if username else None
                    
                    post_code = media.get('code')
                    post_url = f"https://www.instagram.com/p/{post_code}/" if post_code else None

                    latitude = None
                    longitude = None
                    if media.get('location'):
                        location = media.get('location')
                        latitude = location.get('lat')
                        longitude = location.get('lng')

                    post_info = {
                        'timestamp': media.get('taken_at'),
                        'username': username,
                        'user_url': user_url,
                        'post_url': post_url,
                        'caption': media.get('caption', {}).get('text'),
                        'like_count': media.get('like_count'),
                        'comment_count': media.get('comment_count'),
                        'latitude': latitude,
                        'longitude': longitude,
                    }
                    all_posts.append(post_info)
                except (AttributeError, TypeError) as e:
                    print(f"Skipping a post due to parsing error: {e}")
                    continue
            
        return all_posts, next_max_id

    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the request: {e}")
        return [], None
    except json.JSONDecodeError:
        print("Failed to decode JSON from response.")
        return [], None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [], None

def trigger_workflow(hashtag, posts, like_threshold, email):
    github_api_url = "https://api.github.com/repos/prakhar-thecoder/cybershield-hackathon-2025/actions/workflows/social_media_analysis.yml/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ.get('GIHTUB_PAT')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {
        "ref": "main",
        "inputs": {
            "hashtag": hashtag,
            "posts": str(posts),
            "likes_threshold": str(like_threshold),
            "email": email,
            "type": "full"
        }
    }
    
    try:
        response = requests.post(github_api_url, headers=headers, json=payload)
        print(response.text)
        response.raise_for_status()
        print("Workflow triggered successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to trigger workflow: {e}")

if __name__ == '__main__':
    # hashtag_to_search = "freekashmir"
    # posts, next_cursor = get_posts(hashtag_to_search)
    
    # if posts:
    #     print(f"Found {len(posts)} posts for #{hashtag_to_search}")
    #     print(json.dumps(posts, indent=4))
    #     print(f"\nNext cursor for pagination: {next_cursor}")
    # else:
    #     print(f"Could not retrieve posts for #{hashtag_to_search}")
    trigger_workflow("freekashmir", 20, 10, "pnp14072005@gmail.com")
