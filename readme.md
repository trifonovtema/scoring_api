# Scoring API

## Description

Scoring API is an HTTP-based service designed to demonstrate declarative validation and scoring logic. It processes POST
requests with a JSON payload to perform data validation and return responses based on predefined methods.

This project focuses on leveraging object-oriented programming (OOP) principles, including metaclasses, descriptors, and
validation logic.


---

## Project Structure
The project is organized as follows:

### **`src` Directory**
Contains the main logic and modules of the Scoring API:
- **`api.py`**: Main entry point for the HTTP server. Handles incoming requests and routes them to the appropriate handler.
- **`fields.py`**: Contains custom field descriptors (e.g., `CharField`, `PhoneField`, `DateField`) and validation logic for request fields.
- **`handler.py`**: Core logic for handling different API methods (`online_score` and `clients_interests`) and request validation.
- **`requests.py`**: Defines request models and validation rules using custom fields and metaclasses.
- **`scoring.py`**: Provides scoring logic (`get_score`) and mock implementation for fetching client interests (`get_interests`).
- **`settings.py`**: Stores configuration settings such as log settings, response codes, security settings, and gender options.
- **`setup_logs.py`**: Configures the logging system to handle file and console outputs.

### **`tests` Directory**
Contains unit tests for validating the API's behavior:
- **`test.py`**: Test cases for the API methods and field validation.

---


## Requirements

- Python 3.12+
- Poetry for dependency management

## Installation

To install the dependencies, run:

```bash
make install
```

## Running the Server

To start the server:

```bash
make run
```

## Running Tests

To run unit tests:

```bash
make test
```

## Formatting and Typing

To ensure the code adheres to formatting and type-checking standards:

```bash
make format
make typing
```