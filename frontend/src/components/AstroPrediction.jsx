import React, { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Stars, Moon, Sun } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AstroPrediction = () => {
  const [formData, setFormData] = useState({
    birthDate: "",
    birthTime: "",
    city: "",
    latitude: "",
    longitude: "",
    timezone: "",
  });

  const [citySearch, setCitySearch] = useState("");
  const [cityResults, setCityResults] = useState([]);
  const [searchingCity, setSearchingCity] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCitySearch = async (value) => {
    setCitySearch(value);
    
    if (value.length < 2) {
      setCityResults([]);
      return;
    }

    setSearchingCity(true);
    try {
      const response = await axios.post(`${API}/search-city`, {
        query: value,
      });
      setCityResults(response.data);
    } catch (err) {
      console.error("City search error:", err);
      setCityResults([]);
    } finally {
      setSearchingCity(false);
    }
  };

  const handleCitySelect = (city) => {
    setFormData((prev) => ({
      ...prev,
      city: city.name,
      latitude: city.latitude.toString(),
      longitude: city.longitude.toString(),
      timezone: city.timezone.toString(),
    }));
    setCitySearch(city.name);
    setCityResults([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/get-prediction`, {
        birthDate: formData.birthDate,
        birthTime: formData.birthTime,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        timezone: parseFloat(formData.timezone),
      });

      setResult(response.data);
    } catch (err) {
      console.error("Prediction error:", err);
      setError(
        err.response?.data?.detail ||
          "Произошла ошибка при получении прогноза"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Stars className="w-8 h-8 text-purple-400 mr-2" />
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-purple-400 via-violet-400 to-indigo-400 bg-clip-text text-transparent">
              Бесплатный краткий астропрогноз на 2026 год по вашей карте
            </h1>
            <Moon className="w-8 h-8 text-purple-400 ml-2" />
          </div>
          <p className="text-slate-400 text-lg">
            Для подписчиков Берта Маковера
          </p>
        </div>

        {/* Form Card */}
        <Card className="bg-slate-900 border-slate-800 shadow-2xl mb-8" data-testid="prediction-form-card">
          <CardHeader>
            <CardTitle className="text-2xl text-slate-100 flex items-center">
              <Sun className="w-6 h-6 text-amber-400 mr-2" />
              Данные рождения
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Date and Time */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="birthDate" className="text-slate-300">
                    Дата рождения
                  </Label>
                  <Input
                    id="birthDate"
                    name="birthDate"
                    type="date"
                    value={formData.birthDate}
                    onChange={handleInputChange}
                    required
                    className="bg-slate-800 border-slate-700 text-slate-100 mt-2"
                    data-testid="birth-date-input"
                  />
                </div>
                <div>
                  <Label htmlFor="birthTime" className="text-slate-300">
                    Время рождения
                  </Label>
                  <Input
                    id="birthTime"
                    name="birthTime"
                    type="time"
                    value={formData.birthTime}
                    onChange={handleInputChange}
                    required
                    className="bg-slate-800 border-slate-700 text-slate-100 mt-2"
                    data-testid="birth-time-input"
                  />
                </div>
              </div>

              {/* City Search */}
              <div className="relative">
                <Label htmlFor="citySearch" className="text-slate-300">
                  Место рождения (город)
                </Label>
                <Input
                  id="citySearch"
                  type="text"
                  value={citySearch}
                  onChange={(e) => handleCitySearch(e.target.value)}
                  placeholder="Начните вводить название города..."
                  className="bg-slate-800 border-slate-700 text-slate-100 mt-2"
                  data-testid="city-search-input"
                />
                {searchingCity && (
                  <Loader2 className="absolute right-3 top-11 w-5 h-5 animate-spin text-purple-400" />
                )}
                {cityResults.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-slate-800 border border-slate-700 rounded-md shadow-lg max-h-60 overflow-y-auto">
                    {cityResults.map((city, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => handleCitySelect(city)}
                        className="w-full text-left px-4 py-3 hover:bg-slate-700 transition-colors border-b border-slate-700 last:border-b-0"
                        data-testid={`city-result-${index}`}
                      >
                        <div className="text-slate-100">{city.name}</div>
                        <div className="text-sm text-slate-400">
                          {city.country} · Координаты: {city.latitude.toFixed(2)}, {city.longitude.toFixed(2)}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Coordinates and Timezone */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="latitude" className="text-slate-300">
                    Широта
                  </Label>
                  <Input
                    id="latitude"
                    name="latitude"
                    type="number"
                    step="0.0001"
                    value={formData.latitude}
                    onChange={handleInputChange}
                    required
                    className="bg-slate-800 border-slate-700 text-slate-100 mt-2"
                    data-testid="latitude-input"
                  />
                </div>
                <div>
                  <Label htmlFor="longitude" className="text-slate-300">
                    Долгота
                  </Label>
                  <Input
                    id="longitude"
                    name="longitude"
                    type="number"
                    step="0.0001"
                    value={formData.longitude}
                    onChange={handleInputChange}
                    required
                    className="bg-slate-800 border-slate-700 text-slate-100 mt-2"
                    data-testid="longitude-input"
                  />
                </div>
                <div>
                  <Label htmlFor="timezone" className="text-slate-300">
                    Часовой пояс (GMT+/-)
                  </Label>
                  <Input
                    id="timezone"
                    name="timezone"
                    type="number"
                    step="0.5"
                    value={formData.timezone}
                    onChange={handleInputChange}
                    required
                    className="bg-slate-800 border-slate-700 text-slate-100 mt-2"
                    data-testid="timezone-input"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold py-6 text-lg transition-all duration-300"
                data-testid="get-prediction-button"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Получение прогноза...
                  </>
                ) : (
                  <>
                    <Stars className="mr-2 h-5 w-5" />
                    Получить прогноз на 2026 год
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Error Message */}
        {error && (
          <Card className="bg-red-900/20 border-red-800 mb-8" data-testid="error-message">
            <CardContent className="pt-6">
              <p className="text-red-400">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Planets */}
            <Card className="bg-slate-900 border-slate-800 shadow-2xl" data-testid="planets-card">
              <CardHeader>
                <CardTitle className="text-2xl text-slate-100 flex items-center">
                  <Sun className="w-6 h-6 text-amber-400 mr-2" />
                  Положение планет
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.planets.map((planet, index) => (
                    <div
                      key={index}
                      className="bg-slate-800/50 border border-slate-700 rounded-lg p-4"
                      data-testid={`planet-${index}`}
                    >
                      <h3 className="font-semibold text-purple-400 mb-2">
                        {planet.name}
                      </h3>
                      <div className="text-sm text-slate-300 space-y-1">
                        <p>Знак: {planet.sign}</p>
                        <p>Накшатра: {planet.nakshatra}</p>
                        <p>Дом: {planet.house}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Vdasha Periods */}
            {result.vdasha && result.vdasha.length > 0 && (
              <Card className="bg-slate-900 border-slate-800 shadow-2xl" data-testid="vdasha-card">
                <CardHeader>
                  <CardTitle className="text-2xl text-slate-100 flex items-center">
                    <Moon className="w-6 h-6 text-purple-400 mr-2" />
                    Периоды (Махадаша) на 2026 год
                  </CardTitle>
                  <p className="text-sm text-slate-400 mt-2">
                    Расчет по системе Вимшоттари Даша с использованием Саваны года (360 дней)
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {result.vdasha.map((period, index) => (
                      <div
                        key={index}
                        className="bg-slate-800/50 border border-slate-700 rounded-lg p-4"
                        data-testid={`vdasha-period-${index}`}
                      >
                        <h3 className="font-semibold text-indigo-400 mb-2">
                          {period.planet}
                        </h3>
                        <p className="text-sm text-slate-300">
                          {period.start} — {period.end}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Prediction */}
            <Card className="bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 border-purple-800/50 shadow-2xl" data-testid="prediction-card">
              <CardHeader>
                <CardTitle className="text-2xl text-slate-100 flex items-center">
                  <Stars className="w-6 h-6 text-purple-400 mr-2" />
                  Астрологический прогноз на 2026 год
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-200 text-lg leading-relaxed">
                  {result.prediction}
                </p>
              </CardContent>
            </Card>

            {/* CTA Block - Full Forecast */}
            <Card className="bg-gradient-to-br from-purple-900/30 via-indigo-900/30 to-slate-900 border-purple-700/50 shadow-2xl" data-testid="cta-card">
              <CardContent className="pt-8">
                <div className="text-center space-y-6">
                  <h2 className="text-3xl font-bold text-slate-100">
                    Получите полный астрологический прогноз на 2026 год от Берта Маковера
                  </h2>
                  
                  <Button
                    onClick={() => window.open('https://get.vedicastrologyonline.ru/2026', '_blank')}
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold py-6 px-8 text-lg transition-all duration-300"
                    data-testid="full-forecast-button"
                  >
                    <Stars className="mr-2 h-5 w-5" />
                    Заказать полный прогноз
                  </Button>

                  <div className="text-slate-300 text-base leading-relaxed max-w-2xl mx-auto space-y-3">
                    <p>С учётом главного периода, подпериода и подподпериода.</p>
                    <p>По всем основным сферам жизни.</p>
                    <p>Анализ каждого месяца и его влияние на ваше состояние.</p>
                    <p>А также рекомендации и практики для гармонизации неблагоприятного влияния.</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Examples Block */}
            <Card className="bg-slate-900 border-slate-800 shadow-2xl" data-testid="examples-card">
              <CardHeader>
                <CardTitle className="text-2xl text-slate-100 text-center">
                  Примеры прогнозов
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button
                    onClick={() => window.open('https://docs.google.com/document/d/1pUxAPeaNXqFBuXpUkZ7RRxZGg_l6E3oBePHUdQ5aKpE/edit?usp=sharing', '_blank')}
                    variant="outline"
                    className="bg-slate-800 border-slate-700 text-slate-100 hover:bg-slate-700 hover:border-purple-500 py-8 text-base font-medium transition-all duration-300"
                    data-testid="example-brief"
                  >
                    <div className="flex flex-col items-center gap-2">
                      <span className="text-lg font-semibold">Краткий прогноз</span>
                      <span className="text-sm text-slate-400">(текст)</span>
                    </div>
                  </Button>

                  <Button
                    onClick={() => window.open('https://docs.google.com/document/d/1oTqJcEghZgFHY7BqDsk6VC1PqROCJ7W3tbpVgV42RF0/edit?usp=sharing', '_blank')}
                    variant="outline"
                    className="bg-slate-800 border-slate-700 text-slate-100 hover:bg-slate-700 hover:border-purple-500 py-8 text-base font-medium transition-all duration-300"
                    data-testid="example-basic"
                  >
                    <div className="flex flex-col items-center gap-2">
                      <span className="text-lg font-semibold">Базовый прогноз</span>
                      <span className="text-sm text-slate-400">(текст)</span>
                    </div>
                  </Button>

                  <Button
                    onClick={() => window.open('https://kinescope.io/iU3a8qJcruYue4j2GcMvQF', '_blank')}
                    variant="outline"
                    className="bg-slate-800 border-slate-700 text-slate-100 hover:bg-slate-700 hover:border-purple-500 py-8 text-base font-medium transition-all duration-300"
                    data-testid="example-full"
                  >
                    <div className="flex flex-col items-center gap-2">
                      <span className="text-lg font-semibold">Полный прогноз</span>
                      <span className="text-sm text-slate-400">(видео)</span>
                    </div>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default AstroPrediction;