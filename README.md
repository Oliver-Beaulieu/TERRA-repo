# TERRA — Tracking European Climate Risk & Refugee Asylum

TERRA is a web app that links **climate, economic, and asylum data** for the 27 EU member states (2010–2023), so analysts, humanitarian coordinators, and displaced students can explore how climate stress drives forced migration. Climate change — rising temperatures, heatwaves, drought, and flooding — is already pushing people from their homes, yet no single tool brings the climate signals and the displacement data they cause into one place. TERRA fills that gap with role-specific dashboards, interactive maps, and two trained machine-learning models that predict asylum applications and climate stress, all served from a Streamlit front end on top of a Flask + MySQL backend.

>  **Read about how we built it on our blog:** [TERRA Project Blog](ADD_BLOG_URL_HERE)
>


## Features

- **Climate-risk map** — every EU country bucketed into Low / Medium / High / Critical climate-displacement risk, powered by a live ML prediction.
- **Country comparison & profiles** — compare countries side by side and drill into yearly climate, economic, and asylum data for a single nation.
- **Asylum-prediction model** — TERRA Model 1 predicts annual asylum applications for a country from its climate and economic indicators.
- **Climate-prediction model** — TERRA Model 2 predicts heatwave days, heavy-precipitation days, and dry days at once.
- **Displacement timeline & climate events** — track how displacement trends and climate disasters have evolved over time.
- **"Find similar countries"** — surface countries facing climate/displacement pressures like your own.
- **NGO directory** — browse, filter, add, and view profiles for humanitarian organizations.
- **Saved views & report exports** — save country comparisons and export summaries/reports.
- **Role-based dashboards (RBAC)** — three personas (Policy Analyst, Humanitarian Coordinator, Climate-Displaced Student) each see only the tools relevant to them.

## Getting Started

TERRA runs entirely in Docker — you don't need Python, MySQL, or any libraries installed locally, just Docker.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes `docker compose`)
- Git

(For local ML development outside Docker, see [docs/PreReq.md](docs/PreReq.md) for the optional Python environment setup.)

### 1. Clone the repo

```bash
git clone ADD_GIT_CLONE_URL_HERE
cd <repo-folder>
```

> _(Replace `ADD_GIT_CLONE_URL_HERE` with your team repo's clone URL.)_

### 2. Create the `.env` file

The API and MySQL container read their configuration from `api/.env`. Copy the template and fill in real values:

```bash
cp api/.env.template api/.env
```

Then open `api/.env` and set the values:

| Variable | Used by | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | Flask API | Secret used to sign Flask session cookies |
| `DB_USER` | API + MySQL | Database user (defaults to `root`) |
| `DB_HOST` | API | Database hostname (`db`, the compose service name) |
| `DB_PORT` | API | Database port (`3306`) |
| `DB_NAME` | API | Database name (`terra_db`) |
| `MYSQL_ROOT_PASSWORD` | API + MySQL | Root password; the API uses it as the DB password and MySQL uses it to initialize the container |

Do **not** commit `api/.env` or share the password publicly.

### 3. Start the app

```bash
docker compose up -d        # build & start all three containers (app, api, db)
```

The database seeds itself from `database-files/terra_db.sql` on first start — including the 27 countries, their yearly data, and a first set of trained model parameters — so predictions work immediately.

| Service | URL |
|---------|-----|
| Streamlit app | http://localhost:8501 |
| Flask API | http://localhost:4000 |
| MySQL | `localhost:3200` (mapped from container port 3306) |

Other useful commands:

```bash
docker compose down         # stop and remove the containers
docker compose stop         # stop without removing (data is in-memory, so it reseeds on `up`)
docker compose up db -d      # start only the database (swap `db` for `api`/`app`)
```

To pick up edits to the SQL files, run `docker compose down && docker compose up` — the database is ephemeral (tmpfs) and reseeds on every recreate.

## Using the App

1. Open http://localhost:8501. The home screen (`Home.py`) is a **persona login** — pick one of the three roles to enter the app.
2. The sidebar (driven by `app/src/modules/nav.py`) shows only the pages your chosen role can use:
   - **Gabriel — Policy Analyst:** compare countries, review/edit country risk classifications, run the asylum-prediction model, save comparison views, and export reports.
   - **Diana — Humanitarian Coordinator:** view the risk map and priority countries, manage the NGO directory, and export country summaries.
   - **Mohammed — Climate-Displaced Student:** explore the risk map, climate events, the displacement timeline, and find countries similar to his own.
   - **Administrator:** manage and retrain the ML models (defined in the DB and `nav.py`, reached by setting the role directly rather than from a home-page button).
3. From there, follow the sidebar links — e.g. open the **Map** to see live risk levels, **Compare Countries** to put nations side by side, or **Prediction** to run the asylum model on custom inputs.

See [docs/RBAC.md](docs/RBAC.md) for a full explanation of the role-access system and how to adapt it.

## Repository Structure

The repo is organized into six main directories:

- `./app` — the Streamlit front end (role-based dashboards under `app/src/pages`, sidebar logic in `app/src/modules/nav.py`)
- `./api` — the Flask REST API (route blueprints under `api/backend/`, the two TERRA models under `api/backend/ml_models/`)
- `./database-files` — `terra_db.sql`, which creates and seeds the MySQL database (schema, 27 countries, yearly data, and trained model parameters)
- `./datasets` — the raw and processed CSVs (Open-Meteo, Eurostat, World Bank, and the merged training set)
- `./ml-src` — the ML development work: Jupyter notebooks for ingestion/cleaning/EDA/modeling, plus the pure-Python training scripts
- `./docs` — project documentation

The repo also contains a `docker-compose.yaml` that wires up the three containers (front-end app, REST API, and MySQL database).

### Learning the codebase

TERRA follows the standard three-layer web-app pattern, so you can learn it one layer at a time:

1. **`./app`** — the Streamlit front end. Start with `Home.py` (the persona login) and `modules/nav.py` (which decides each role's sidebar links), then open a few numbered pages in `pages/` to see how they call the API and render results.
2. **`./api`** — the application-logic layer. Each feature lives in its own blueprint under `api/backend/` (`countries`, `climate`, `risk`, `policy`, `ngos`, `views`, `prediction`); `rest_entry.py` wires them together. This layer talks to the database and serves the ML predictions.
3. **`./database-files/terra_db.sql`** — defines every table, seeds the 27 EU countries and their yearly data, and stores the trained model parameters the API reads at prediction time.
4. **`./ml-src`** — the notebooks show how data was ingested, cleaned, explored, and modeled; the pure-Python scripts are the production versions.

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

## The Machine-Learning Models

TERRA includes **two** trained predictive models. Both follow a *DB-served parameter* pattern: the model is trained offline, but its fitted weights (coefficients, intercept, and scaler statistics) are stored in the database, and the API reconstructs the prediction from those rows at request time.

1. Raw data comes from three sources — Open-Meteo (climate), Eurostat (asylum applications), and the World Bank (economic/demographic) — and is ingested, cleaned, and merged in the `ml-src/` notebooks into `datasets/processed/merged_data.csv`.
2. The production training/prediction code lives in `api/backend/ml_models/`:
   - **TERRA Model 1** (`terra_model_1.py`) — a linear regression that predicts **annual asylum applications** for a country. Inputs are `country_code` plus `gdp_per_capita`, `unemployment_rate`, `temp_mean`, `heatwave_days`, `precip_days_heavy`, and `dry_days`. It trains on `log1p(asylum_applications)` using 2010–2018 data and is evaluated on 2019–2023. Several features (raw `year`, `population`, `urban_pct`, `precip_total`, `evapotrans_total`) were intentionally dropped during tuning for multicollinearity / out-of-range extrapolation reasons documented in the file.
   - **TERRA Model 2** (`terra_model_2.py`) — a multivariate linear regression that predicts **three climate variables at once** (`heatwave_days`, `precip_days_heavy`, `dry_days`) from `gdp_per_capita`, `unemployment_rate`, `population`, `urban_pct`, `asylum_applications`, and `country_code`.
3. Trained parameters are written to the database by each model's `store_params_in_db()` function and read back by `predict()`:
   - Model 1 → `model1_params`, `model1_scaler`
   - Model 2 → `model2_params`, `model2_scaler`, `model2_encoder`
   - These tables are seeded with a first set of parameters in `database-files/terra_db.sql`, so prediction works the moment the database comes up.
4. Retraining is exposed to the **Administrator** role: the `POST /model1/train` and `POST /model2/train` routes call `train_test_model()` and then `store_params_in_db()`, writing a new versioned row (the latest `sequence_number` wins). The `.joblib` dumps under `outputs/` are kept only as offline evaluation artifacts.
5. In Streamlit, the asylum model is driven from `app/src/pages/11_Prediction.py`, which collects the input features, posts them to `/predict/asylum`, and displays the predicted asylum count. The risk map (`02_Map_Demo.py`) and classification pages use `/predict/asylum-map`, which buckets each country's prediction into Low / Medium / High / Critical risk levels. The admin pages (`21_ML_Model_Mgmt.py`, `22_Prettier_ML.py`) cover retraining and the observed-vs-predicted view.

## The Team

 See **[sub-README.md](sub-README.md)** for a recap of each member's contributions.

## More Documentation

- [docs/PreReq.md](docs/PreReq.md) — optional local Python environment setup for ML development
- [docs/RBAC.md](docs/RBAC.md) — how the role-based access control system works
- [docs/ImportantTips.md](docs/ImportantTips.md) — hot reloading, recovering from container crashes, and working with the MySQL container
