# Smart Resume Screener

A web application for parsing resumes and matching candidates to job descriptions using semantic similarity and machine learning.

## Features

- Resume parsing from PDF and DOCX files
- Candidate ranking based on job requirements
- Semantic matching using sentence transformers
- User authentication and authorization
- Admin panel for managing users and job descriptions

## Prerequisites

- Python 3.8 or higher
- MySQL database
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd smart-resume-screener
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the required environment variables (see Configuration section below)

5. Run database migrations:
   ```
   python run_migration.py
   ```

6. Create an admin user:
   ```
   python create_admin.py
   ```

7. Start the application:
   ```
   python app.py
   ```

## Configuration

The application requires the following environment variables to be set:

- `DATABASE_URL`: MySQL database connection string (e.g., "mysql://username:password@localhost/database_name")
- `SESSION_SECRET`: Secret key for session management (should be a random string)
- `EMBEDDING_MODEL`: (Optional) Sentence transformer model name (default: "all-MiniLM-L6-v2")

Example .env file:
```
DATABASE_URL=mysql://root:password@localhost/smartscreener
SESSION_SECRET=your-secret-key-here
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Usage

1. Register a new user account or log in with the admin account (username: admin, password: admin123)
2. Upload resumes through the web interface
3. Create job descriptions with required skills and education
4. View ranked candidates for each job description

## Development

To run the application in development mode:
```
python app.py
```

The application will be available at http://localhost:5000

## Testing

Run the evaluation harness to test the ranking algorithms:
```
python -m evaluation.harness
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Harshal Dhangar# SmartScreener
