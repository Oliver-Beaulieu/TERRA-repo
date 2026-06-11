# Contributors to TERRA

### Oliver Beaulieu
#### Data ingestion
- Collected and saved raw datasets (Eurostat, Open-Meteo, WorldBank) into `datasets/raw/` using data ingestion notebook I built in `ml-src/01_data_ingestion.ipynb`

#### Data cleaning & EDA
- Data cleaning notebook `ml-src/02_data_cleaning.ipynb`
- EDA and plot visualizations on merged dataset `ml-src/03_eda_visualizations.ipynb`; set up `outputs/` folder to store plots (correlation heatmap, QQ plot, risidual plot, time series, country averages, avg vs. predicted).

#### Model 1: Asylum prediction
- Developed model 1 in notebook `ml-src/04_model_1.ipynb` with breakdown analysis, validations and assumption checks.
- Later converted model into a runnable Python script `ml-src/model_1.py / model1_pipeline.py`. 
- Added actual vs. predicted graph during Phase 2 revision.

#### Model integration 
- Stored model weights and parameters in database `database-files/terra_db.sql`.
- Updated UI to match model's new input feature set in `app/src/pages/11_Prediction.py`.

#### Documentation and About page
- Updated `README.md` from template
- Added my bio and photo to about page `app/src/pages/30_About.py`.
