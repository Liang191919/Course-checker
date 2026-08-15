"""
Invoke tasks for Course-checker project.
Cross-platform task runner.

Usage:
    inv dev        - Run bot locally with Python
    inv build      - Build Docker image
    inv start      - Run Docker container
    inv format     - Run Ruff format on the project
"""

from invoke import task

from logging_config import configure_logging, logger

configure_logging()


@task
def dev(c):
    """Run bot locally with Python."""
    logger.info("🚀 Running bot locally...")
    c.run("python main.py")


@task
def build(c):
    """Build Docker image locally."""
    logger.info("🔨 Building Docker image...")
    c.run("docker build -t course-checker .")
    logger.info("✅ Build complete!")


@task
def start(c):
    """Run Docker container."""
    build(c)
    logger.info("🚀 Running container...")
    c.run("docker run --env-file .env course-checker")


@task
def format(c):
    """Format project files with Ruff."""
    logger.info("🔧 Formatting project with Ruff...")
    c.run("ruff format .")
