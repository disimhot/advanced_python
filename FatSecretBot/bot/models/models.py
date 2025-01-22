from pydantic import BaseModel, ValidationError, ConfigDict, Field, Extra

class MainWeatherData(BaseModel, extra='allow'):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    sea_level: int
    grnd_level: int

class WeatherResponse(BaseModel, extra='allow'):
    main: MainWeatherData
