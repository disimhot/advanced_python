import pandas as pd
import streamlit as st
import requests
from config import TOKEN
import asyncio
import matplotlib.pyplot as plt
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")
import nest_asyncio

nest_asyncio.apply()

st.set_page_config(page_title="Прогноз погоды", layout="centered")
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


async def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def analyze_city_trend(city_data, season, window_size=30):
    city = city_data['city'].iloc[0]
    st.subheader(f'Сезонный профиль погоды в городе и сезонe: {city}, {season}')
    try:
        # Статистика
        city_data['min_temp'] = city_data.groupby('season', group_keys=False)['temperature'].transform('min')
        city_data['max_temp'] = city_data.groupby('season', group_keys=False)['temperature'].transform('max')
        city_data['std'] = city_data.groupby('season', group_keys=False)['temperature'].transform('std')
        city_data['mean'] = city_data.groupby('season', group_keys=False)['temperature'].transform('mean')

        city_data['rolling_mean'] = (
            city_data.groupby('season', group_keys=False)
            .apply(lambda group: group['temperature'].rolling(window=window_size).mean())
        )
        city_data['rolling_std'] = (
            city_data.groupby('season', group_keys=False)
            .apply(lambda group: group['temperature'].rolling(window=window_size).std())
        )
        city_data['anomaly'] = (city_data['temperature'] > city_data['rolling_mean'] + 2 * city_data['rolling_std']) | (
                city_data['temperature'] < city_data['rolling_mean'] - 2 * city_data['rolling_std'])

        return city_data[city_data['season'] == season]
    except Exception as e:
        print(f'Произошла ошибка при построении графика: {e}')


def plot_city_trend(city_data):
    try:
        ticks = city_data['day_month'].unique()[::10]
        x = city_data['day_month'].unique()
        mean = city_data.groupby('day_month')['temperature'].mean()
        up = mean + 2 * city_data.groupby('day_month')['temperature'].std()
        down = mean - 2 * city_data.groupby('day_month')['temperature'].std()

        fig = plt.figure(
            figsize=(8, 8),
            facecolor='whitesmoke',
            dpi=200
        )

        plt.plot(
            x, mean,
            color='green',
            alpha=1,
            linewidth=0.5,
            label='Температура'
        )

        plt.plot(
            x, up,
            color='brown',
            alpha=0.7,
            linewidth=1,
            linestyle='--',
            label='Верхняя граница'
        )

        plt.plot(
            x, down,
            color='brown',
            alpha=0.7,
            linewidth=1,
            linestyle='--',
            label='Нижняя граница'
        )

        plt.xlabel(
            'Даты',
            fontdict=dict(family='serif', color='darkred', weight='normal', size=10)
        )
        plt.xticks(ticks, rotation=90)

        plt.ylabel(
            'Средняя температура',
            fontdict=dict(family='serif', color='darkred', weight='light', size=10)
        )

        plt.legend(
            loc='lower right',
            borderaxespad=0.5
        )
        plt.grid(True)
        st.pyplot(fig)
    except Exception as e:
        print(f'Произошла ошибка при построении графика: {e}')


def plot_city_season_year_anomalies(city_data_year, year):
    x = city_data_year['day_month']
    ticks = city_data_year['day_month'][::10]
    anomalies = city_data_year['anomaly']

    st.subheader(f'Аномальные точки в году {year}')
    fig = plt.figure(
        figsize=(8, 8),
        facecolor='whitesmoke',
        dpi=200
    )

    plt.plot(
        x,
        city_data_year['temperature'],
        color='blue',
        alpha=1,
        linewidth=0.5,
        label='Температура'
    )
    plt.plot(
        x, city_data_year['min_temp'],
        color='lightsteelblue',
        linestyle=':',
        alpha=1,
        linewidth=2,
        label='Минимальная температура'
    )
    plt.plot(
        x, city_data_year['max_temp'],
        color='lightsteelblue',
        linestyle=':',
        alpha=1,
        linewidth=2,
        label='Максимальная температура'
    )
    plt.plot(
        x,
        city_data_year['rolling_mean'],
        color='green',
        alpha=1,
        linewidth=0.5,
        linestyle='--',
        label='Средняя температура со окном 30 дней'
    )

    plt.scatter(
        x[anomalies],  # x values where anomaly is True
        city_data_year['temperature'][anomalies],  # corresponding temperature values
        color='red',
        label='Аномалии'
    )

    plt.xlabel(
        'Даты',
        fontdict=dict(family='serif', color='darkred', weight='normal', size=10)
    )
    plt.xticks(ticks, rotation=90)

    plt.ylabel(
        f'Температура {year}',
        fontdict=dict(family='serif', color='darkred', weight='light', size=10)
    )

    plt.legend(
        loc='lower right',
        borderaxespad=0.5
    )
    plt.grid(True)
    st.pyplot(fig)


def get_season_by_month(month):
    for season, months in MONTH_SEASONS.items():
        if month in months:
            return season
    return None


def check_anomalies(city_data, current_weather):
    current_day = datetime.now().day
    current_month = datetime.now().month
    season = get_season_by_month(current_month)

    city_data['std'] = city_data.groupby('season', group_keys=False)['temperature'].transform('std')
    city_data['mean'] = city_data.groupby('season', group_keys=False)['temperature'].transform('mean')
    temp_data = city_data[(city_data['day'] == current_day) & (city_data['month'] == current_month)].reset_index()
    print('current_weather', current_weather)
    print('temp_datamean][0] ', temp_data['mean'][0] )
    print('temp_datastd][0] ', temp_data['std'][0] )
    has_anomaly = (current_weather > temp_data['mean'][0] + 2 * temp_data['std'][0]) | (
            current_weather < temp_data['mean'][0] - 2 * temp_data['std'][0])

    if has_anomaly:
        st.warning("Внимание! Температура на текущей дате выходит за пределы допустимых значений.")
    else:
        st.success("Температура сегодня не является аномальной")


async def main():
    st.title("Прогноз погоды")
    city = st.selectbox("Choose city", CITIES)
    # Load the cleaned file
    df = pd.read_csv(RAW_DATA_URL)

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day_month'] = df['timestamp'].dt.strftime('%d-%b')
    df['day'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['year'] = df['timestamp'].dt.year
    city_df = df[df['city'] == city]
    weather = None
    if st.button("Получить текущую погоду"):
        weather = await get_weather(city)
        temperature = weather['main']['temp']
        st.success(f"Температура в {city}: {temperature}°C")
        check_anomalies(city_df, temperature)

    season = st.selectbox("Choose season", SEASONS)

    city_data = analyze_city_trend(city_df, season)
    plot_city_trend(city_data)

    year = st.selectbox("Choose year", city_df['timestamp'].dt.year.unique())
    city_data_year = city_data[city_data['year'] == year]

    plot_city_season_year_anomalies(city_data_year, year)


if __name__ == "__main__":
    asyncio.run(main())
