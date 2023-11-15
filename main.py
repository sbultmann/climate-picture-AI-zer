from openai import OpenAI
import dotenv
import os
import requests
import json
from datetime import date
import shutil # save img locally
from time import time
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-lon", help="longitude for weather forecast", type=float, required=True)
parser.add_argument("-lat", help="latitude for weather forecast", type=float, required=True)
parser.add_argument("-o", help="output directory", required=True)

args = parser.parse_args()


dotenv.load_dotenv()
LAT = args.lat
LON = args.lon
OUTDIR = args.o
OPENWEATHER_API = os.environ['OPENWEATHER_API']
STYLE = "japanese watercolor greyscale with red"


def get_weather(lat, lon, OPENWEATHER_API):
    
    datum = str(date.today())
    print(datum)
    url = f'https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={datum}&units=metric&appid={OPENWEATHER_API}'
    response_API = requests.get(url)
    data = json.loads(response_API.text)
    """except:
        data = None"""
    return data

def generate_gpt4_prompt(data, style):
    text =    f"""
    Generate a creative prompt in the style of {style} based on the weatherforecast with the following information:
    Coordinates: {data['lon']} longitude; {data['lat']}
    Precipitation: {data['precipitation']['total']} mm
    Temperature: {data['temperature']['max']} Celsius
    Pressure: {data['pressure']['afternoon']} hPa
    Relative Humidity: {data['humidity']['afternoon']} %
    Clouds: {data['cloud_cover']['afternoon']} %
    Date: {date.today()}
    Make sure the coordinates are translated into a country and/or an area in a country. Be es precise as possible.
    The prompt should be as detailed as possible to convey the style and artistic represenation and mood of the weather.
    It is strictly important that no text is shown on the image. State this clearly in the prompt!
    """
    return text

def generate_dalle_prompt(gpt_prompt, chat_protocol = None):
    messages=[
        {"role": "system", "content": "You are a prompt engineer that specializes in creating prompts for the image generating AI Dall-E3."},
        {"role": "user", "content": gpt_prompt}
        ]
    client = OpenAI()

    response = client.chat.completions.create(
        temperature = 1.3,
        model="gpt-4-1106-preview",
        messages=messages,
    )
    return response.choices[0].message.content

def generate_image(dalle_prompt):
    client = OpenAI()
    response = client.images.generate(
    model="dall-e-3",
    prompt=dalle_prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )
    image_url = response.data[0].url
    return image_url

def save_image(image_url, file_name, out_dir):
    res = requests.get(image_url, stream = True)

    if res.status_code == 200:
        with open(f'{out_dir}/{file_name}','wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image sucessfully Downloaded: ',file_name)
    else:
        print('Image Couldn\'t be retrieved')

def save_prompt(prompt, file_name, out_dir):
    with open(f'{out_dir}/{file_name}', "w") as f:
        f.write(prompt)


import os
if not os.path.exists(OUTDIR):
   os.makedirs(OUTDIR)

weather = get_weather(LAT, LON, OPENWEATHER_API)



print(weather)
gpt_prompt = generate_gpt4_prompt(weather, STYLE)
print(gpt_prompt)
dalle_prompt = generate_dalle_prompt(gpt_prompt)
print(dalle_prompt)

image_url = generate_image(dalle_prompt)
print(image_url)
now = time()
save_image(image_url, f'{date.today()}-{now}.png', OUTDIR)
save_prompt(dalle_prompt, f'DALL-E3.{date.today()}-{now}.txt', OUTDIR)
save_prompt(gpt_prompt, f'GPT4.{date.today()}-{now}.txt', OUTDIR)

#-lon 11.5755 -lat 48.1374

