# TERRA — Tracking European Climate Risk & Refugee Asylum

TERRA is a Streamlit + Flask web app that links climate, economic, and asylum data for the 27 EU member states (2010–2023) so analysts, humanitarian coordinators, and displaced students can explore the relationship between climate stress and forced migration. It is built for CS 4973 (Summer 2026 Belgium DoC) and ships with two trained machine-learning models, a seeded MySQL database, and role-specific dashboards.

## Prerequisites

See [docs/PreReq.md](docs/PreReq.md) for full setup instructions, including Python environment setup with Anaconda/Miniconda or the standard Python virtual environment tool, required tools, and IDE configuration.

## Structure of the Repo

- This repository is organized into six main directories:
  - `./app` - the Streamlit app (role-based dashboards under `app/src/pages`, sidebar logic in `app/src/modules/nav.py`)
  - `./api` - the Flask REST API (route blueprints under `api/backend/`, the two TERRA models under `api/backend/ml_models/`)
  - `./database-files` - `terra_db.sql`, which creates and seeds the MySQL database (schema, 27 countries, yearly data, and trained model parameters)
  - `./datasets` - the raw and processed CSVs (Open-Meteo, Eurostat, World Bank, and the merged training set)
  - `./ml-src` - the ML development work: Jupyter notebooks for ingestion/cleaning/EDA/modeling, plus the pure-Python training scripts
  - `./docs` - project documentation

- The repo also contains a `docker-compose.yaml` file that is used to set up the Docker containers for the front end app, the REST API, and MySQL database.

## Suggestion for Learning the Project Code Base

If you are not familiar with web app development, this code base might be confusing. But don't worry — TERRA follows the standard three-layer pattern, so you can learn it one layer at a time:

1. Start by exploring the `./app` directory. This is the Streamlit front end. Begin with `Home.py` (the login screen, where you pick a persona) and `modules/nav.py` (which decides what sidebar links each role sees), then open a few of the numbered pages in `pages/` to see how they call the API and render the results.
1. Next, explore the `./api` directory. Each feature lives in its own blueprint under `api/backend/` (`countries`, `climate`, `risk`, `policy`, `ngos`, `views`, `prediction`). `rest_entry.py` wires them all together. This is the "application logic" layer that talks to the database and serves the ML predictions.
1. Then, explore `./database-files/terra_db.sql`. It defines every table, seeds the 27 EU countries and their yearly climate/economic/asylum data, and stores the trained model parameters that the API reads at prediction time.
1. Finally, look at `./ml-src`. The notebooks show how the data was ingested, cleaned, explored, and modeled; the pure-Python scripts are the versions that get used in production.
1. Bonus: If you want a totally separate copy of the repo on your laptop to experiment with without affecting your team repo, see the *Setting Up a Personal Sandbox Repo* section in [docs/RepoSetup.md](docs/RepoSetup.md).

## Setting Up the Repos

See [docs/RepoSetup.md](docs/RepoSetup.md) for full instructions on forking and configuring the team repo, setting up the `.env` file, and running the Docker containers. An optional section there also covers setting up a personal sandbox repo for individual experimentation.

## Environment Variables

The API reads its configuration from `api/.env` (the MySQL container reads the same file via `env_file`). Copy `api/.env.template` to `api/.env` and fill in real values. In production (Coolify), these are set in the Coolify UI instead of a file.

| Variable | Used by | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | Flask API | Secret used to sign Flask session cookies |
| `DB_USER` | API + MySQL | Database user (defaults to `root`) |
| `DB_HOST` | API | Database hostname (`db`, the compose service name) |
| `DB_PORT` | API | Database port (`3306`) |
| `DB_NAME` | API | Database name (`terra_db`) |
| `MYSQL_ROOT_PASSWORD` | API + MySQL | Root password; the API uses it as the DB password and MySQL uses it to initialize the container |

`WATCHPACK_POLLING=true` is set on the `app` and `api` containers in `docker-compose.yaml` (not in `.env`) to make hot reloading work reliably inside Docker.

## Important Tips

See [docs/ImportantTips.md](docs/ImportantTips.md) for tips on hot reloading, recovering from container crashes, and working with the MySQL container (including how to update your SQL files and recreate the database).

## Deployment

Each team's fork is automatically deployed to the course Coolify server (`coolify.cs4535.cloud`) on every push to `main`. Each team picks its own name and gets a dedicated Coolify team they can log in to; apps are reachable at `<team-name>.neu-in-leuven.cloud`.

- Students: see [docs/StudentDeployment.md](docs/StudentDeployment.md).
- Staff (per-team onboarding checklist): see [docs/Deployment.md](docs/Deployment.md).

## Handling User Role Access and Control

TERRA uses a simple Role-based Access Control (RBAC) system implemented in Streamlit. From `Home.py` you log in as one of three personas; the chosen role is stored in `st.session_state` and `modules/nav.py` renders only the sidebar links that role is allowed to use. The database (`roles`/`users` tables) defines a fourth role, `administrator`, whose pages exist in the app but who has no login button on the home screen.

The personas are:

- **Gabriel — Policy Analyst** (`policy_analyst`): compares countries, reviews and edits country risk classifications, runs the asylum-prediction model, saves country comparison views, and exports reports.
- **Diana — Humanitarian Coordinator** (`humanitarian_coordinator`): views the risk map and priority countries, manages the NGO directory (browse, add, view profiles), and exports country summaries.
- **Mohammed — Climate-Displaced Student** (`student_user`): explores the risk map, climate events, the displacement timeline, and finds countries similar to his own.
- **Administrator** (`administrator`): manages the ML models (the train/retrain and observed-vs-predicted pages). Defined in the database and in `nav.py`, but reached by setting the role directly rather than from a home-page button.

See [docs/RBAC.md](docs/RBAC.md) for a full explanation of how the RBAC system works and step-by-step instructions for adapting it.

## REST API Routes

The API is assembled in `api/backend/rest_entry.py`, which registers one blueprint per feature. The main routes are:

**Countries** (`api/backend/countries/country_routes.py`)
- `GET /countries` — all countries
- `GET /countries/<country_id>` — one country profile
- `GET /countries/<country_id>/year-data` — yearly climate/economic/asylum rows for a country

**Climate** (`api/backend/climate/climate_routes.py`)
- `GET /countries/<country_id>/climate-events` — climate events for a country

**Risk** (`api/backend/risk/risk_routes.py`)
- `GET /risk-classifications` — all country risk assessments
- `PUT /risk-classifications/<country_id>` — update a country's risk score/level for a year

**Policy** (`api/backend/policy/policy_routes.py`)
- `GET /policies`, `POST /policies`, `PUT /policies/<policy_id>`, `DELETE /policies/<policy_id>`
- `POST /policy-flags`, `PUT /policy-flags/<flag_id>`, `DELETE /policy-flags/<flag_id>`

**NGOs** (`api/backend/ngos/ngo_routes.py`)
- `GET /ngo/ngos` (optional `country`, `focus_area`, `founding_year` filters), `GET /ngo/ngos/<ngo_id>`
- `POST /ngo/ngos`, `PUT /ngo/ngos/<ngo_id>`, `DELETE /ngo/ngos/<ngo_id>`

**Saved Views** (`api/backend/views/view_routes.py`)
- `GET /saved-views` (optional `user_id` filter), `GET /saved-views/<view_id>`
- `POST /saved-views`, `PUT /saved-views/<view_id>`, `DELETE /saved-views/<view_id>`

**ML predictions** (`api/backend/prediction/terra_model_routes.py`)
- `POST /predict/asylum`, `POST /model1/train` — TERRA Model 1
- `GET /predict/asylum-map` (optional `?year=`) — bulk asylum predictions for every country, used by the risk map
- `POST /predict/climate`, `POST /model2/train` — TERRA Model 2
- `GET /predict/climate-map` (optional `?year=`) — bulk climate predictions for every country
- `POST /prediction` (`api/backend/prediction/prediction_routes.py`) — a thin wrapper that calls the `ml-src/model_1.py` script directly

## Incorporating a Predictive ML Model into your Project

TERRA includes **two** trained predictive models. Both follow a *DB-served parameter* pattern: the model is trained offline, but its fitted weights (coefficients, intercept, and scaler statistics) are stored in the database, and the API reconstructs the prediction from those rows at request time. Nothing is hard-coded in the prediction function.

1. The raw data comes from three sources — Open-Meteo (climate), Eurostat (asylum applications), and the World Bank (economic/demographic) — and is ingested, cleaned, and merged in the `ml-src/` notebooks into `datasets/processed/merged_data.csv`.
1. The production training/prediction code lives in `api/backend/ml_models/`:
   - **TERRA Model 1** (`terra_model_1.py`) — a linear regression that predicts **annual asylum applications** for a country. Inputs are `country_code` plus `gdp_per_capita`, `unemployment_rate`, `temp_mean`, `heatwave_days`, `precip_days_heavy`, and `dry_days`. It trains on `log1p(asylum_applications)` using 2010–2018 data and is evaluated on 2019–2023; the output is the predicted number of asylum applications. Several features (raw `year`, `population`, `urban_pct`, `precip_total`, `evapotrans_total`) were intentionally dropped during tuning for multicollinearity / out-of-range extrapolation reasons documented in the file.
   - **TERRA Model 2** (`terra_model_2.py`) — a multivariate linear regression that predicts **three climate variables at once** (`heatwave_days`, `precip_days_heavy`, `dry_days`) from `gdp_per_capita`, `unemployment_rate`, `population`, `urban_pct`, `asylum_applications`, and `country_code`.
1. Trained parameters are written to the database by each model's `store_params_in_db()` function and read back by `predict()`:
   - Model 1 → `model1_params`, `model1_scaler`
   - Model 2 → `model2_params`, `model2_scaler`, `model2_encoder`
   - These tables are seeded with a first set of parameters in `database-files/terra_db.sql`, so prediction works the moment the database comes up.
1. Retraining is exposed to the **Administrator** role: the `POST /model1/train` and `POST /model2/train` routes call `train_test_model()` and then `store_params_in_db()`, writing a new versioned row (the latest `sequence_number` wins). The `.joblib` dumps under `outputs/` are kept only as offline evaluation artifacts.
1. In Streamlit, the asylum model is driven from `app/src/pages/11_Prediction.py`, which collects the model's input features, posts them to `/predict/asylum`, and displays the predicted asylum count. The risk map (`02_Map_Demo.py`) and classification pages consume the bulk `/predict/asylum-map` route, which buckets each country's prediction into Low / Medium / High / Critical risk levels. The admin pages (`21_ML_Model_Mgmt.py`, `22_Prettier_ML.py`) cover retraining and the observed-vs-predicted view.
