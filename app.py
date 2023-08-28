import time
from flask import Flask, request, render_template, redirect, url_for, session
from flask_session import Session
import csv

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.static_folder = 'static'  # Specify the directory for static files
Session(app)

def get_last_sender_ip():
    try:
        with open('data/last_sender_ip.txt', 'r') as ip_file:
            return ip_file.read().strip()
    except FileNotFoundError:
        return None

def set_last_sender_ip(ip):
    with open('data/last_sender_ip.txt', 'w') as ip_file:
        ip_file.write(ip)


def get_words():
    with open('words.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        words = list(csv_reader)
    return words

@app.route('/')
def index():
    last_sender_ip = get_last_sender_ip()
    words = get_words()

    return render_template('index.html',
                           words=words,
                           last_sender_ip=last_sender_ip)

@app.route('/add_word', methods=['POST'])
def add_word():
    MIN_TIME_BETWEEN_ACTIONS = 10  # Set your desired time interval (in seconds)

    last_action_time = session.get('last_action_time', 0)
    current_time = time.time()
    time_elapsed = current_time - last_action_time

    if time_elapsed < MIN_TIME_BETWEEN_ACTIONS:
        error_message = "Please wait before adding another word."
        return render_template('index.html',
                               error_message=error_message,
                               words=get_words(),
                               last_sender_ip=get_last_sender_ip())

    session['last_action_time'] = current_time

    new_word = request.form['word'].strip()
    words = new_word.split()

    if len(words) != 1:
        error_message = "Please enter only one word."
        return render_template('index.html',
                               error_message=error_message,
                               words=get_words(),
                               last_sender_ip=get_last_sender_ip())

    last_sender_ip = get_last_sender_ip()
    forwarded_ip = request.headers.get('X-Forwarded-For')

    if last_sender_ip == forwarded_ip:
        error_message = "You cannot send consecutive words."
        return render_template('index.html',
                               error_message=error_message,
                               words=get_words(),
                               last_sender_ip=last_sender_ip)

    with open('words.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([new_word])

    set_last_sender_ip(forwarded_ip)

    last_word_message = "The last word was added."

    return render_template('index.html',
                           last_word_message=last_word_message,
                           words=get_words(),
                           last_sender_ip=last_sender_ip)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
