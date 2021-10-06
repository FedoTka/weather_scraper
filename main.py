from bs4 import BeautifulSoup
import requests
import re
import itertools
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.graphics.vertex_instructions import Rectangle
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock


headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }

urls = {
        'Glubokoe': 'https://www.gismeteo.by/weather-glubokoye-11028/10-days/',
        'Minsk': 'https://www.gismeteo.by/weather-minsk-4248/10-days/',
        'Borisov': 'https://www.gismeteo.by/weather-borisov-4235/10-days/',
        'Baranovichi': 'https://www.gismeteo.by/weather-baranovichi-4263/10-days/',
        'Bereza': 'https://www.gismeteo.by/weather-beryoza-11196/10-days/',
        'Lida': 'https://www.gismeteo.by/weather-lida-4244/10-days/',
        'Grodno': 'https://www.gismeteo.by/weather-grodno-4243/10-days/',
        'Mogilev': 'https://www.gismeteo.by/weather-mogilev-4251/10-days/',
        'Brest': 'https://www.gismeteo.by/weather-brest-4912/10-days/',
}

class Scraper(GridLayout):

        def __init__(self,urls, headers, images, **kwargs):
                super(Scraper, self).__init__(**kwargs)

                ##Получаю URLs и заголовки
                self.urls = urls
                self.headers = headers

                #Добавляю словарь с картинками и начальный фон
                self.images = images
                self.standart_image = 'standart.png'


                ## Настройка начального фона для экрана
                with self.canvas:
                        self.rect = Rectangle(source=self.standart_image, pos=[0, 0], size=[800, 600])

                ##Указываю количество колонок на LayOut
                self.cols = 2

                #Создание всех кнопок
                self.Main_Label = Label(text='Weather', font_size=60)
                self.mainbutton = Button(text='Select day', size_hint=(None, None), height=50)
                self.button_regions = Button(text='Select region', size_hint=(None, None), height=50)

                ##Добавляем все на экран
                self.add_widget(self.mainbutton)
                self.add_widget(self.button_regions)
                self.add_widget(self.Main_Label)

                ##Словарь для информации о погоде
                self.data = dict()
                self.picture = dict()

                try:

                        # Создаю выпадающее меню выбора даты
                        self.dropdown = DropDown()
                        self.mainbutton.bind(on_release=self.dropdown.open)
                        self.dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))


                        ## Меню выбора городов
                        self.dropdown_regions = DropDown()
                        self.dropdown_regions.bind(on_select=lambda instance, x: setattr(self.button_regions, 'text', x))

                        for region in self.urls.keys():
                                btn = Button(text=region, size_hint_y=None, font_size=14, height=55)
                                btn.bind(on_release=lambda btn: self.dropdown_regions.select(btn.text))

                                btn.bind(on_press=lambda btn: self.get_request(f'{self.urls[btn.text]}'))
                                self.dropdown_regions.add_widget(btn)


                        self.button_regions.bind(on_release=self.dropdown_regions.open)


                except Exception as Ex:
                        self.Except = Ex
                        print(Ex)
                        self.Main_Label.text = 'Some Error, try later :('

        #Добавляем кнопки к выпадающему меню
        def add_data_buttons(self):
                for day in self.days:
                        btn = Button(text=f'{day}', size_hint_y=None, font_size=14, height=55)
                        btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
                        btn.bind(on_release=lambda btn: setattr(self.rect, 'source', self.picture.get(btn.text)))
                        self.dropdown.add_widget(btn)


        # Запрос по выбранному url
        def get_request(self, url):
                try:
                        self.data_html = requests.get(url, headers=self.headers).text

                        self.soup = BeautifulSoup(self.data_html, 'lxml')

                        self.scrap_days()
                        self.scrap_weather()
                        self.scrap_wind()
                        self.scrap_temperature()
                        self.add_data_buttons()

                        #Записываем данные в словарь
                        for weather, day, wind, day_temp, night_temp in zip(self.weather, self.days, self.wind,
                                                                            self.day_temperature,
                                                                            self.night_temperature):
                                sep ='\n'
                                rest = weather.split(sep, 1)[0]
                                print(rest)
                                self.picture.update({f'{day}': self.images[rest]})
                                self.data.update({f'{day}': [weather, 'Дневная tC:' + f'{day_temp}',
                                                             'Ночная tC:' + f'{night_temp}',
                                                             'Скорость ветра:' + f'{wind}']})
                except Exception as Ex:
                        self.Except = Ex
                        print(Ex)
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
                try:
                        days = self.soup.find('div',class_='widget-row-days-date').find_all('div', class_='date')
                        self.days = [re.sub(r'[ \n]', '', x.text) for x in days]
                        return self.days
                except:
                        print('scrap_days')
        # Получаем общие комментарии о погоде
        def scrap_weather(self):
                try:
                        #weather = self.soup.find_all('span', class_='tooltip')
                        weather = self.soup.find_all('div', class_='tooltip')
                        self.weather = [re.sub(r', ', '\n', x.get('data-text')) for x in weather]
                        return self.weather
                except:
                        print('scrap_weather')
        # Данные о температуре
        def scrap_temperature(self):
                try:
                        temp_soup_day = self.soup.find('div', class_='widget-row-chart-temperature').find_all('div', class_='maxt')
                        self.day_temperature = [x.find('span').text for x in temp_soup_day]
                        temp_soup_night = self.soup.find('div', class_='widget-row-chart-temperature').find_all('div', class_='mint')
                        self.night_temperature = [x.find('span').text for x in temp_soup_night]

                        return {'day': self.day_temperature, 'night': self.night_temperature}
                except:
                        print('scrap_tempr')
        # Скорость ветра
        def scrap_wind(self):
                try:
                        #wind = self.soup.find('div', class_='widget__row_wind-or-gust').find_all('span', class_='unit_wind_m_s')
                        wind = self.soup.find('div', class_='widget-row-wind-gust').find_all('span',class_='unit_wind_m_s')

                        self.wind = [re.sub(r'[ \n]', '', x.text) for x in wind]

                        return self.wind
                except:
                        print('scrap_wind')

class WeatherApp(App):
        def build(self):
                scraper = Scraper(urls=urls, headers=headers, images={'Ясно': 'sun.png',
                                                                      'Облачно': 'cloud.png',
                                                                      'Переменная облачность': 'cloud.png',
                                                                      'Пасмурно': 'rain.png'})

                Clock.schedule_interval(scraper.print_data, 1.0 / 60.0)
                return scraper

def main():
        WeatherApp().run()


if __name__ == '__main__':
        main()