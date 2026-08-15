# Course-checker

This project is a Python automation script that monitors course seat availability on Polytechnique Montréal’s student portal (Dossier Étudiant) and sends real-time notifications to a Discord server when seats become available. It combines web scraping / HTTP requests, session authentication, asynchronous execution, and Discord bot integration.

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd Course-checker
```

### 2. Create the `.env` file

Create a ­`.env­` file based on the example file ­`.env.example­`.

Then, edit ­­­`.env` and replace the placeholder values with your actual values:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
CHANNEL_ID=your_channel_id_here
LOG_CHANNEL_ID=your_log_channel_id_here
USER_ID_TO_PING=your_user_id_here
DOSSIER_USER=your_username_here
DOSSIER_PASS=your_password_here
BIRTH=your_birth_date_here
COURSES=course_codes_here
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run locally

```bash
python main.py
```

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
