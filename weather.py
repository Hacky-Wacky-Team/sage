#weather imports https://www.geeksforgeeks.org/how-to-extract-weather-data-from-google-in-python/
import requests
from bs4 import BeautifulSoup

# Function to get weather data from Google
def get_weather_data(userLocation):
  url = "https://www.google.com/search?q=weather+" + userLocation
  html = requests.get(url).content
  soup = BeautifulSoup(html, 'html.parser')
  temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
  data = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text.split('\n')
  time = data[0]
  sky = data[1]
  
  # getting all div tag
  listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
  strd = listdiv[5].text

  # getting other required data
  pos = strd.find('Wind')
  other_data = strd[pos:]

  # printing all data
  print("Temperature is", temp)
  print("Time: ", time)
  print("Sky Description: ", sky)
  weather_data = [temp, time, sky]
  return weather_data