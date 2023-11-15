FROM python:3.10

COPY . .

RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y cron

# Add the cron job
RUN crontab -l | { cat; echo "0 5 * * * bash "; } | crontab -

CMD cron ; python -m http.server --directory out