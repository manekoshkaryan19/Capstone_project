# Capstone_project
Capstone Application

The Capstone Application is a Trello REST API implementation. This README outlines how to set up the environment, run tests.

## Prerequisites

Docker

Docker Compose

Setting Up the Testing Environment

## Clone the Repository:

git clone https://github.com/manekoshkaryan19/Capstone_project.git

cd capstone_project

## Start Docker Services:
```
docker-compose build 

docker-compose up -d

```
## Running Tests

Unit Tests

python -m unittest discover -s tests/test_unit

Integration Tests

python -m unittest discover -s tests/test_integration

Or pytest for both:

pytest

Test Coverage

Run Tests with Coverage:

coverage run -m unittest discover

Generate Coverage Report:

coverage report

# Without Docker

Clone the Repository:

Create a Virtual Environment:

python3 -m venv venv

source venv/bin/activate  

Install Dependencies:

pip install -r requirements.txt

## Configuration

Environment Variables:
Create a .env file in the root directory and add the following configurations:

SECRET_KEY=your_secret_key

JWT_SECRET_KEY=your_jwt_secret_key

DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/your_database

Ensure to replace the placeholders with your values

## Database Setup:

Production Database: Ensure PostgreSQL is installed and a database is created as specified in DATABASE_URL.

Testing Database: The testing environment uses an in-memory SQLite database, so no additional setup is required.

## Running the Application

Initialize the Database:

flask db init

flask db migrate -m "Initial migration."

flask db upgrade

Run the Application:

python app.py

The application will be accessible at http://localhost:5000.

## Testing

Install Test Dependencies:

pip install pytest coverage

The next setps are the same as above.
