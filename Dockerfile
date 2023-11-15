FROM python:3.10

COPY . .

RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y cron

# Add the cron job
RUN crontab -l | { cat; echo "0 5 * * * python main.py -lon 11.5755 -lat 48.1374 -o out"; } | crontab -

CMD cron ; python -m http.server --directory out