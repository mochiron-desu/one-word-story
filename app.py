import time
from flask import Flask, request, render_template, redirect, url_for, session
from flask_session import Session
import csv

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.static_folder = 'static'
Session(app)

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
        print(f"Error writing last sender IP: {e}")

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

    if time_elapsed < MIN_TIME_BETWEEN_ACTIONS:
        error_message = "Please wait before adding another word."
        return redirect_with_error('index', error_message)

    session['last_action_time'] = current_time

    new_word = request.form['word'].strip()
    words = new_word.split()

    if len(words) != 1:
        error_message = "Please enter only one word."
        return redirect_with_error('index', error_message)

    last_sender_ip = get_last_sender_ip()
    forwarded_ip = request.headers.get('X-Forwarded-For')

    if last_sender_ip == forwarded_ip:
        error_message = "You cannot send consecutive words."
        return redirect_with_error('index', error_message)

    with open('words.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([new_word])

    set_last_sender_ip(forwarded_ip)

    return redirect_with_error('index', "")  # Redirect back to the main page

def redirect_with_error(route, error_message):
    session['error_message'] = error_message
    return redirect(url_for(route))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
