# One-Word Story Game

Welcome to the One-Word Story Game project! This is a simple web application written in Python using the Flask framework. Players can collaboratively build a story one word at a time.

## Features

- Players can add one word to the story in turns.
- Health checker periodically monitors server health and sends logs to a Discord webhook.
- Basic session management to prevent abuse and spam.
- Minimalistic front-end using Flask templates.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- Flask-Session

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mochiron-desu/one-word-story.git
   cd one-word-story
   ```

2. Install dependencies:

   ```bash
   pip install Flask Flask-Session
   ```

3. Run the application:

   ```bash
   python app.py
   ```

5. Access the application in your browser at `http://localhost:8080`.

## Usage

- Players can visit the homepage and add one word to the ongoing story.
- The application enforces a time interval between word additions to prevent spam.
- The health checker monitors the server's health and logs results to a Discord webhook.

## Contributing

Contributions are welcome! If you find a bug or want to improve the project, feel free to open an issue or submit a pull request.


## Acknowledgements

- This project was inspired by the concept of collaborative storytelling.
- Built using Flask, a lightweight web framework in Python.
