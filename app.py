from flask import Flask, request, render_template, redirect, url_for
import csv

app = Flask(__name__)

@app.route('/')
def index():
    with open('words.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        words = list(csv_reader)
    
    return render_template('index.html', words=words)

@app.route('/add_word', methods=['POST'])
def add_word():
    new_word = request.form['word'].strip()  # Remove leading/trailing whitespace
    words = new_word.split()  # Split input into words
    
    if len(words) != 1:
        error_message = "Please enter only one word."
        return render_template('index.html', error_message=error_message)
    
    with open('words.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([new_word])
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
