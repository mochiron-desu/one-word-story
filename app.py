from flask import Flask, request, render_template, redirect, url_for
import csv
#ss
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


def get_nickname():
  try:
    with open('data/nickname.txt', 'r') as nickname_file:
      return nickname_file.read().strip()
  except FileNotFoundError:
    return None


def set_nickname(nickname):
  with open('data/nickname.txt', 'w') as nickname_file:
    nickname_file.write(nickname)


def get_words():
  with open('words.csv', 'r') as csvfile:
    csv_reader = csv.reader(csvfile)
    words = list(csv_reader)
  return words


@app.route('/')
def index():
  last_sender_ip = get_last_sender_ip()
  words = get_words()
  nickname = get_nickname() or 'Anonymous'

  return render_template('index.html',
                         words=words,
                         last_sender_ip=last_sender_ip,
                         nickname=nickname)


@app.route('/set_nickname', methods=['POST'])
def set_nickname_route():
  new_nickname = request.form['nickname'].strip()
  if new_nickname:
    set_nickname(new_nickname)
  return redirect(url_for('index'))


@app.route('/add_word', methods=['POST'])
def add_word():
  new_word = request.form['word'].strip()
  words = new_word.split()

  if len(words) != 1:
    error_message = "Please enter only one word."
    return render_template('index.html',
                           error_message=error_message,
                           words=get_words(),
                           last_sender_ip=get_last_sender_ip(),
                           nickname=get_nickname())

  last_sender_ip = get_last_sender_ip()
  current_ip = request.remote_addr

  if last_sender_ip == current_ip:
    error_message = "You cannot send consecutive words."
    return render_template('index.html',
                           error_message=error_message,
                           words=get_words(),
                           last_sender_ip=last_sender_ip,
                           nickname=get_nickname())

  with open('words.csv', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow([new_word])

  set_last_sender_ip(current_ip)

  nickname = get_nickname() or 'Anonymous'
  last_word_message = f"{nickname} added the last word."

  return render_template('index.html',
                         last_word_message=last_word_message,
                         words=get_words(),
                         last_sender_ip=last_sender_ip,
                         nickname=nickname)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)