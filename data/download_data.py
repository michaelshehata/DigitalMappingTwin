import kaggle
import os

kaggle.api.authenticate()

kaggle.api.dataset_download_files(
    'sudalairajkumar/daily-temperature-of-major-cities',
    path='raw/data', 
    unzip=True
)