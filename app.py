from flask import Flask, request, render_template, redirect, url_for
import csv

#changees mad

app = Flask(__name__)

def get_last_sender_ip():
    try:
        with open('data/last_sender_ip.txt', 'r') as ip_file:
            return ip_file.read().strip()
    except FileNotFoundError:
        return None

def set_last_sender_ip(ip):
    with open('data/last_sender_ip.txt', 'w') as ip_file:
        ip_file.write(ip)

@app.route('/')
def index():
    last_sender_ip = get_last_sender_ip()
    words = get_words()
    
    return render_template('index.html', words=words, last_sender_ip=last_sender_ip)


@app.route('/add_word', methods=['POST'])
def add_word():
    new_word = request.form['word'].strip()
    words = new_word.split()
    
    if len(words) != 1:
        error_message = "Please enter only one word."
        return render_template('index.html', error_message=error_message, words=get_words(), last_sender_ip=get_last_sender_ip())

    last_sender_ip = get_last_sender_ip()
    current_ip = request.remote_addr
    
    if last_sender_ip == current_ip:
        error_message = "You cannot send consecutive words."
        return render_template('index.html', error_message=error_message, words=get_words(), last_sender_ip=last_sender_ip)

    with open('words.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([new_word])

    set_last_sender_ip(current_ip)
    
    return redirect(url_for('index'))

def get_words():
    with open('words.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        words = list(csv_reader)
    return words


if __name__ == '__main__':
    app.run(debug=True)
