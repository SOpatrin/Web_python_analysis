from io import StringIO

import pandas
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException

from analysis import Analysis

app = FastAPI()
analysis = Analysis(pandas.read_csv('owid-covid-data.csv'))


@app.post('/data')
async def post_data(file: UploadFile = File(...)):
    global analysis
    analysis = Analysis(pandas.read_csv(StringIO(str(file.file.read(), 'utf-8')), encoding='utf-8'))
    return {'filename': file.filename}


@app.get('/')
def read_root():
    return 'hello'


@app.get('/countries')
def get_countries():
    return analysis.get_countries()


@app.get('/countries/{country}/quantile')
def get_quantile(country: str):
    if country not in analysis.countries:
        raise HTTPException(404, 'No such country')
    return analysis.get_quantile(country)


@app.get('/countries/{country}/delta/{delta}')
def get_countries_by_delta(country: str, delta: float):
    if country not in analysis.countries:
        raise HTTPException(404, 'No such country')
    return analysis.get_countries_by_delta(country, delta)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")
