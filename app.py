import os
import time
from flask import Flask, request, render_template, redirect, url_for, session
from flask_session import Session
import csv
import threading
import requests
import schedule
import datetime

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.static_folder = 'static'
Session(app)

WEBHOOK_URL = os.environ['WEBHOOK_URL']

def health_check_and_log():
    while True:
        print("Entered Health Check")
        # Perform a health check request to your server
        try:
            response = requests.get("https://one-word-story.mochirondesu.repl.co/")  # Adjust the URL as needed
            if response.status_code == 200:
                message = "Server is healthy."
            else:
                message = f"Health check failed. Status code: {response.status_code}"
        except requests.RequestException as e:
            message = f"Health check failed. Error: {e}"

        # Send log message to the Discord webhook
        payload = {
            "content": f"[Health Check] {message}"
        }
        webhook_response = requests.post(WEBHOOK_URL, json=payload)
        if webhook_response.status_code != 204:
            print("Failed to send health check log to webhook")

        # Wait for the specified interval before performing the next health check
        time.sleep(60 * 10)  # Adjust the interval (in seconds) as needed

# Function to send log messages to the Discord webhook
def send_log_to_webhook(message):
    payload = {
        "content": message
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print("Failed to send log to webhook")

def get_last_sender_ip():
    try:
        with open('data/last_sender_ip.txt', 'r') as ip_file:
            return ip_file.read().strip()
    except FileNotFoundError:
        return None

def set_last_sender_ip(ip):
    try:
        with open('data/last_sender_ip.txt', 'w') as ip_file:
            ip_file.write(ip)
    except Exception as e:
        send_log_to_webhook(f"Error writing last sender IP: {e}")

def get_words():
    with open('words.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        words = list(csv_reader)
    return words

@app.route('/')
def index():
    last_sender_ip = get_last_sender_ip()
    words = get_words()
    error_message = session.pop('error_message', None)  # Retrieve and clear error message from session

    return render_template('index.html',
                           words=words,
                           last_sender_ip=last_sender_ip,
                           error_message=error_message)

@app.route('/add_word', methods=['POST'])
def add_word():
    MIN_TIME_BETWEEN_ACTIONS = 10  # Set your desired time interval (in seconds)

    last_action_time = session.get('last_action_time', 0)
    current_time = time.time()
    time_elapsed = current_time - last_action_time
    forwarded_ip = request.headers.get('X-Forwarded-For')
    new_word = request.form['word'].strip()
    words = new_word.split()

    if time_elapsed < MIN_TIME_BETWEEN_ACTIONS:
        error_message = "Please wait before adding another word."
        send_log_to_webhook(f"`{forwarded_ip}` Tried to send multiple requests before cooldown. Words: `{words}`")
        return redirect_with_error('index', error_message)

    session['last_action_time'] = current_time


    if len(words) != 1:
        error_message = "Please enter only one word."
        send_log_to_webhook(f"`{forwarded_ip}` Tried to send mutiple words. Words: `{words}`")
        return redirect_with_error('index', error_message)

    last_sender_ip = get_last_sender_ip()

    if last_sender_ip == forwarded_ip:
        error_message = "You cannot send consecutive words."
        send_log_to_webhook(f"`{forwarded_ip}` tried to send consecutive words. Words: `{words}`")
        return redirect_with_error('index', error_message)

    with open('words.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([new_word])
        send_log_to_webhook(f"`{forwarded_ip}` addded the word `{new_word}`")

    set_last_sender_ip(forwarded_ip)

    return redirect_with_error('index', "")  # Redirect back to the main page

@app.route('/view_story/<month_year>')
def view_story_month_year(month_year):
    try:
        with open(f'data/{month_year}_words.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            words = list(csv_reader)
            print(words)
        return render_template('view_story.html', words=words, month_year=month_year)
    except FileNotFoundError:
        error_message = "Story not found for the selected month and year."
        return redirect_with_error('index', error_message)

@app.route('/story_archive')
def story_archive():
    months = get_existing_months()
    return render_template('story.html', months=months)

def get_existing_months():
    months = []
    for filename in os.listdir('data'):
        if filename.endswith("_words.csv"):
            month = filename.split("_words.csv")[0]
            months.append(month)
    return months

def redirect_with_error(route, error_message):
    session['error_message'] = error_message
    return redirect(url_for(route))

def save_words_for_previous_month():
    now = datetime.datetime.now()
    last_month = now.replace(day=1) - datetime.timedelta(days=1)
    last_month_name = last_month.strftime("%B_%Y")

    words = get_words()
    with open(f'data/{last_month_name}_words.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for word in words:
            csv_writer.writerow(word)
        send_log_to_webhook(f"Saved the data to {last_month_name}_words.csv")

def schedule_daily_task():
    send_log_to_webhook("Started Daily Task")
    schedule.every().day.at('00:00').do(save_words_for_previous_month)
    send_log_to_webhook("Completed Daily Task")

if __name__ == '__main__':
    # Start the health checker thread
    health_checker_thread = threading.Thread(target=health_check_and_log)
    health_checker_thread.daemon = True  # Allow the thread to exit when the main program exits
    health_checker_thread.start()

    schedule_daily_task()
  
    # Start the Flask application
    app.run(host='0.0.0.0', port=8080, debug=True)