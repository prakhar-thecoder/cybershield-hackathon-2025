from jinja2 import Environment, FileSystemLoader
import os
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import pandas as pd
import plotly.express as px
import io, base64

async def prepare_report_async(hashtag):
    # Create output directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)

    # Define file paths
    filename_pdf = f"outputs/{hashtag}_report.pdf"
    filename_html = f"outputs/{hashtag}_report.html"

    data = {}
    data['hashtags'] = hashtag
    data['platforms'] = "Instagram"
    data['date_and_time'] = datetime.now().strftime("%d-%m-%Y at %H:%M:%S")

    data['total_posts'] = len(pd.read_csv(f"outputs/{hashtag}_all_posts.csv"))
    data['anti_india_posts'] = len(pd.read_csv(f"outputs/{hashtag}_anti_india_posts.csv"))
    data['threat_level'] = int(pd.read_csv(f"outputs/{hashtag}_anti_india_posts.csv")['threat_score'].mean())
    
    data['user_post_counts'] = pd.read_csv(f"outputs/{hashtag}_user_post_counts.csv").to_dict(orient='records')[:10]
    df_for_graph = pd.DataFrame(data['user_post_counts'])
    df_for_graph['username'] = df_for_graph['username'].apply(lambda x: x[:10] + '...' if len(x) > 10 else x)
    fig = px.bar(
        df_for_graph,
        x="username",
        labels={"username": "Username", "post_count": "No. of Posts"},
        y="post_count",
        color="username",
        title="Top 10 Users by No. of Posts"
    )
    fig.update_layout(showlegend=False)
    buf = io.BytesIO()
    fig.write_image(buf, format="png")
    buf.seek(0)
    data['user_post_counts_graph'] = base64.b64encode(buf.read()).decode("utf-8")

    data['user_reach'] = pd.read_csv(f"outputs/{hashtag}_user_reach.csv").to_dict(orient='records')[:10]
    df_for_graph = pd.DataFrame(data['user_reach'])
    df_for_graph['username'] = df_for_graph['username'].apply(lambda x: x[:10] + '...' if len(x) > 10 else x)
    fig = px.bar(
        df_for_graph,
        x="username",
        labels={"username": "Username", "total_reach": "Reach Score"},
        y="total_reach",
        color="username",
        title="Top 10 Users by Reach"
    )
    fig.update_layout(showlegend=False)
    buf = io.BytesIO()
    fig.write_image(buf, format="png")
    buf.seek(0)
    data['user_reach_graph'] = base64.b64encode(buf.read()).decode("utf-8")
    
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')
    rendered_html = template.render(data=data)

    with open(filename_html, 'w', encoding="utf-8") as f:
        f.write(rendered_html)

    html_path = os.path.abspath(filename_html)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Set the viewport to a standard desktop resolution
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Navigate to the local HTML file
        await page.goto(f'file://{html_path}')
        
        await page.pdf(
            path=filename_pdf, 
            width='1536px', 
            height='2000px', 
            print_background=True
        )
        
        await browser.close()

    return filename_pdf

if __name__ == "__main__":
    hashtag = "kashmirbanegapakistan"
    
    # Run the asynchronous function
    pdf_file = asyncio.run(prepare_report_async(hashtag))
    
    print(f"Report generated: {pdf_file}")
