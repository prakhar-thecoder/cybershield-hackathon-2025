from flask import Flask, render_template, request, redirect, url_for
import email_utils
import request_utils

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        hashtag = request.form.get('hashtag')
        platform = request.form.get('platform')
        num_posts = request.form.get('num_posts')
        email = request.form.get('email')
        print(f"Hashtag: {hashtag}")
        print(f"Platform: {platform}")
        print(f"No. of Posts: {num_posts}")
        print(f"Email: {email}")
        
        request_utils.trigger_workflow(hashtag, num_posts, 20, email)
        email_utils.send_acknowledgment_email(email, hashtag)

        return redirect(url_for('success'))
    return render_template('index.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    if request.method == 'POST':
        email = request.form.get('email')
        print(f"Email: {email}")
        
        email_utils.send_demo_email(email)
        return redirect(url_for('demo_success'))
    return render_template('demo.html')


@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/demo-success')
def demo_success():
    return render_template('demo_success.html')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)