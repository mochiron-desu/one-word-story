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
    new_word = request.form['word']
    
    with open('words.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([new_word])
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
