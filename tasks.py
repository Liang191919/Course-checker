"""
Invoke tasks for Course-checker project.
Cross-platform task runner.

Usage:
    inv dev        - Run bot locally with Python
    inv build      - Build Docker image
    inv start      - Run Docker container
"""

from invoke import task


@task
def dev(c):
    """Run bot locally with Python."""
    print("🚀 Running bot locally...")
    c.run("python main.py")


@task
def build(c):
    """Build Docker image locally."""
    print("🔨 Building Docker image...")
    c.run("docker build -t course-checker .")
    print("✅ Build complete!")


@task
def start(c):
    """Run Docker container."""
    build(c)
    print("🚀 Running container...")
    c.run("docker run --env-file .env course-checker")
