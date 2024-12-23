import pandas as pd
import streamlit as st
import requests
from config import TOKEN
from pydantic import BaseModel, ValidationError, ConfigDict, Field
from typing import List, Optional, Dict
import asyncio
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
import numpy as np
import nest_asyncio

# Suppress warnings
warnings.filterwarnings("ignore")
nest_asyncio.apply()

# Streamlit Configurations
st.set_page_config(page_title="Прогноз погоды", layout="centered")

# Constants
API_KEY = TOKEN
CITIES = ['New York', 'London', 'Paris', 'Tokyo', 'Moscow', 'Sydney',
          'Berlin', 'Beijing', 'Rio de Janeiro', 'Dubai', 'Los Angeles',
          'Singapore', 'Mumbai', 'Cairo', 'Mexico City']
SEASONS = ['spring', 'summer', 'autumn', 'winter']
RAW_DATA_URL = 'https://raw.githubusercontent.com/disimhot/advanced_python/main/streamlit_app/temperature_data.csv'
MONTH_SEASONS = {
    'winter': [1, 2, 3],
    'spring': [4, 5, 6],
    'summer': [7, 8, 9],
    'autumn': [10, 11, 12]
}

# Pydantic Models
class MainWeatherData(BaseModel):
    temp: float = Field(..., description="Температура в градусах Цельсия")

class WeatherResponse(BaseModel):
    main: MainWeatherData

class CityData(BaseModel):
    city: str
    timestamp: pd.Timestamp
    temperature: float
    day: int
    month: int
    year: int
    day_month: str
    model_config = ConfigDict(arbitrary_types_allowed=True)

# Utility Functions
def get_season_by_month(month: int) -> Optional[str]:
    for season, months in MONTH_SEASONS.items():
        if month in months:
            return season
    return None

def fetch_weather(city: str) -> Optional[WeatherResponse]:
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        weather_data = WeatherResponse.parse_obj(response.json())
        return weather_data
    except (requests.RequestException, ValidationError) as e:
        st.error(f"Ошибка при получении погоды: {e}")
        return None

def check_anomalies(city_data: pd.DataFrame, current_weather: float):
    current_day = datetime.now().day
    current_month = datetime.now().month

    city_data['std'] = city_data.groupby('season', group_keys=False)['temperature'].transform('std')
    city_data['mean'] = city_data.groupby('season', group_keys=False)['temperature'].transform('mean')

    temp_data = city_data[(city_data['day'] == current_day) & (city_data['month'] == current_month)].reset_index()

    if not temp_data.empty:
        mean_temp = temp_data['mean'].iloc[0]
        std_temp = temp_data['std'].iloc[0]

        if current_weather > mean_temp + 2 * std_temp or current_weather < mean_temp - 2 * std_temp:
            st.warning("Внимание! Температура на текущей дате выходит за пределы допустимых значений.")
        else:
            st.success("Температура сегодня не является аномальной")

# Analysis Functions
def analyze_city_trend(city_data: pd.DataFrame, season: str, window_size: int = 30) -> pd.DataFrame:
    try:
        city_data['season'] = city_data['month'].apply(get_season_by_month)
        city_data['min_temp'] = city_data.groupby('season')['temperature'].transform('min')
        city_data['max_temp'] = city_data.groupby('season')['temperature'].transform('max')
        city_data['std'] = city_data.groupby('season')['temperature'].transform('std')
        city_data['mean'] = city_data.groupby('season')['temperature'].transform('mean')
        city_data['rolling_mean'] = (
            city_data.groupby('season')['temperature']
            .transform(lambda x: x.rolling(window=window_size).mean())
        )
        city_data['rolling_std'] = (
            city_data.groupby('season')['temperature']
            .transform(lambda x: x.rolling(window=window_size).std())
        )
        city_data['anomaly'] = (
            (city_data['temperature'] > city_data['rolling_mean'] + 2 * city_data['rolling_std']) |
            (city_data['temperature'] < city_data['rolling_mean'] - 2 * city_data['rolling_std'])
        )

        return city_data[city_data['season'] == season]
    except Exception as e:
        st.error(f"Ошибка анализа данных: {e}")
        return pd.DataFrame()

# Plotting Functions
def plot_city_trend(city_data: pd.DataFrame):
    try:
        ticks = city_data['day_month'].unique()[::10]
        x = city_data['day_month'].unique()
        mean = city_data.groupby('day_month')['temperature'].mean()
        up = mean + 2 * city_data.groupby('day_month')['temperature'].std()
        down = mean - 2 * city_data.groupby('day_month')['temperature'].std()

        fig = plt.figure(figsize=(8, 8), facecolor='whitesmoke', dpi=200)

        plt.plot(x, mean, color='green', alpha=1, linewidth=0.5, label='Температура')
        plt.plot(x, up, color='brown', alpha=0.7, linewidth=1, linestyle='--', label='Верхняя граница')
        plt.plot(x, down, color='brown', alpha=0.7, linewidth=1, linestyle='--', label='Нижняя граница')

        plt.xlabel('Даты', fontdict=dict(family='serif', color='darkred', weight='normal', size=10))
        plt.xticks(ticks, rotation=90)
        plt.ylabel('Средняя температура', fontdict=dict(family='serif', color='darkred', weight='light', size=10))

        plt.legend(loc='lower right', borderaxespad=0.5)
        plt.grid(True)
        st.pyplot(fig)
    except Exception as e:
        print(f'Произошла ошибка при построении графика: {e}')


def plot_city_season_year_anomalies(data: pd.DataFrame, year: int):
    try:
        x = np.array(data.day_month)
        ticks = x[::10]
        anomalies = np.array(data.anomaly)

        st.subheader(f'Аномальные точки в году {year}')
        fig = plt.figure(figsize=(8, 8), facecolor='whitesmoke', dpi=200)

        # Температура
        plt.plot(
            x, data.temperature,
            color='blue',
            alpha=1,
            linewidth=0.5,
            label='Температура'
        )

        # Минимальная температура
        plt.plot(
            x, data.min_temp,
            color='lightsteelblue',
            linestyle=':',
            alpha=1,
            linewidth=2,
            label='Минимальная температура'
        )

        # Максимальная температура
        plt.plot(
            x, data.max_temp,
            color='lightsteelblue',
            linestyle=':',
            alpha=1,
            linewidth=2,
            label='Максимальная температура'
        )

        # Скользящее среднее
        plt.plot(
            x, data.rolling_mean,
            color='green',
            alpha=1,
            linewidth=0.5,
            linestyle='--',
            label='Средняя температура со окном 30 дней'
        )

        # Аномалии
        plt.scatter(
            x[anomalies],  # x-значения, где есть аномалии
            np.array(data.temperature)[anomalies],  # Соответствующие значения температуры
            color='red',
            label='Аномалии'
        )

        # Настройки осей
        plt.xlabel(
            'Даты',
            fontdict=dict(family='serif', color='darkred', weight='normal', size=10)
        )
        plt.xticks(ticks, rotation=90)

        plt.ylabel(
            f'Температура {year}',
            fontdict=dict(family='serif', color='darkred', weight='light', size=10)
        )

        # Легенда и сетка
        plt.legend(loc='lower right', borderaxespad=0.5)
        plt.grid(True)

        # Показ графика через Streamlit
        st.pyplot(fig)
    except Exception as e:
        print(f'Произошла ошибка при построении графика: {e}')

# Main Application Logic
async def main():
    st.title("Прогноз погоды")

    city = st.selectbox("Выберите город", CITIES)
    season = st.selectbox("Выберите сезон", SEASONS)

    try:
        df = pd.read_csv(RAW_DATA_URL, parse_dates=['timestamp'])
        df['day_month'] = df['timestamp'].dt.strftime('%d-%b')
        df['day'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['year'] = df['timestamp'].dt.year

        city_df = df[df['city'] == city]

        if st.button("Получить текущую погоду"):
            weather = fetch_weather(city)
            if weather:
                temperature = weather.main.temp
                st.success(f"Температура в {city}: {temperature}°C")
                check_anomalies(city_df, temperature)

        city_data = analyze_city_trend(city_df, season)
        if not city_data.empty:
            plot_city_trend(city_data)

        year = st.selectbox("Выберите год", sorted(city_df['year'].unique()))
        city_data_year = city_data[city_data['year'] == year]
        if not city_data_year.empty:
            plot_city_season_year_anomalies(city_data_year, year)

    except Exception as e:
        st.error(f"Ошибка выполнения: {e}")

if __name__ == "__main__":
    asyncio.run(main())
