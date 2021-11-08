FROM python:3.9-slim-buster

# Create dir. for the bot
WORKDIR /acmupmvoting_bot

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy all the files
COPY . .

# Run the bot
CMD ["python3", "acmvoting-bot/acmvoting-bot.py"]
