# Course-checker

This project is a Python automation script that monitors course seat availability on Polytechnique Montréal’s student portal (Dossier Étudiant) and sends real-time notifications when seats become available. It can notify through either Discord or email, depending on the configuration.

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd Course-checker
```

### 2. Create the `.env` file

Create a `.env` file based on the example file `.env.example`.

Then, edit `.env` and replace the placeholder values with your actual values.

> When `USE_EMAIL=true`, the bot sends the notification by email instead of Discord. For Gmail, use an app password rather than your normal account password.

### 3. Install dependencies

Create and activate a virtual environment (the commands depend on your OS), then install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run locally

```bash
python -m app.main
```

or through Invoke:

```bash
inv dev
```

> There are some more commands available in `tasks.py`.

## Docker image publishing and deployment

The GitHub Actions pipeline pushes the image to Docker Hub as:

```text
<DOCKERHUB_USERNAME>/course-checker:latest
```

where `DOCKERHUB_USERNAME` is defined in the repository Actions variables.

The current published image is:

```bash
docker pull dragonbyte1/course-checker:latest
```

This image can be used for deployment and needs to be run **with the appropriate environment variables**.
