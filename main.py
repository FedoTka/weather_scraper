from bs4 import BeautifulSoup
import requests
import re
import itertools
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivy.clock import Clock


headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }

class Scraper(GridLayout):

        def __init__(self, url, headers, **kwargs):
                super(Scraper, self).__init__(**kwargs)

                self.url = url
                self.headers = headers

                try:
                        # Get-запрос и получения объекта soup
                        self.data = requests.get(self.url, headers= self.headers).text
                        self.soup = BeautifulSoup(self.data, 'lxml')



                        #Получаю все необходимые данные
                        self.scrap_days()
                        self.scrap_weather()
                        self.scrap_wind()
                        self.scrap_temperature()

                        self.data = {

                        }
                        for weather, day, wind, day_temp, night_temp in zip(self.weather, self.days, self.wind, self.day_temperature,
                                                                            self.night_temperature):
                                self.data.update({f'{day}': [weather, 'Дневная tC:'+f'{day_temp}', 'Ночная tC:'+f'{night_temp}', 'Скорость ветра:'+f'{wind}']})


                        self.cols = 1

                        # Создаю выпадающее меню
                        self.dropdown = DropDown()
                        for day in self.days:

                                btn = Button(text= f'{day}', size_hint_y=None, font_size=14, height = 55)
                                btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
                                self.dropdown.add_widget(btn)

                        self.mainbutton = Button(text='Select day', size_hint=(None, None), height = 50)
                        self.mainbutton.bind(on_release=self.dropdown.open)
                        self.dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
                        self.add_widget(self.mainbutton)


                        self.Main_Label = Label(text='Hello', font_size=60)
                        self.add_widget(self.Main_Label)




                except Exception as Ex:
                        self.Except = Ex
                        self.Main_Label.text = 'Some Error, try later :('

        # Вывожу данные в UI
        def print_data(self, dt):
                temp_str=''

                try:
                        for inf in self.data.get(self.mainbutton.text):
                                temp_str += f'\n{inf}'
                        self.Main_Label.text = temp_str
                except Exception as ex:
                        return

        ##Получаем список дат
        def scrap_days(self):
                days = self.soup.find('div', class_='widget__body').find_all('span', class_='w_date__date')
                self.days = [re.sub(r'[ \n]', '', x.text) for x in days]
                return self.days

        # Получаем общие комментарии о погоде
        def scrap_weather(self):
                weather = self.soup.find_all('span', class_='tooltip')
                self.weather = [re.sub(r', ', '\n', x.get('data-text')) for x in weather]
                return self.weather

        # Данные о температуре
        def scrap_temperature(self):
                temp_soup_day = self.soup.find('div', class_='templine w_temperature').find_all('div', class_='maxt')
                self.day_temperature = [x.find('span').text for x in temp_soup_day]
                temp_soup_night = self.soup.find('div', class_='templine w_temperature').find_all('div', class_='mint')
                self.night_temperature = [x.find('span').text for x in temp_soup_night]

                return {'day': self.day_temperature, 'night': self.night_temperature}

        # Скорость ветра
        def scrap_wind(self):
                wind = self.soup.find('div', class_='widget__row_wind-or-gust').find_all('span', class_='unit_wind_m_s')
                self.wind = [re.sub(r'[ \n]', '', x.text) for x in wind]
                return self.wind


class WeatherApp(App):
        def build(self):
                scraper = Scraper(url='https://www.gismeteo.by/weather-borisov-4235/10-days/', headers=headers)
                Clock.schedule_interval(scraper.print_data, 1.0 / 60.0)
                return scraper

def main():
        WeatherApp().run()



if __name__ == '__main__':
        main()