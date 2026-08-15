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

#### Discord mode (default)

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
CHANNEL_ID=your_channel_id_here
LOG_CHANNEL_ID=your_log_channel_id_here
USER_ID_TO_PING=your_user_id_here
USE_EMAIL=false
COURSE_POLLING_SECONDS=10
SESSION_RETRY_SECONDS=3
DOSSIER_USER=your_username_here
DOSSIER_PASS=your_password_here
BIRTH=your_birth_date_here
COURSES=course_codes_here
```

#### Email mode

```env
USE_EMAIL=true
COURSE_POLLING_SECONDS=10
SESSION_RETRY_SECONDS=3
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=your_recipient_email@example.com
DOSSIER_USER=your_username_here
DOSSIER_PASS=your_password_here
BIRTH=your_birth_date_here
COURSES=course_codes_here
```

> When `USE_EMAIL=true`, the bot sends the notification by email instead of Discord. For Gmail, use an app password rather than your normal account password.

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
