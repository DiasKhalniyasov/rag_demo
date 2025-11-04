# Law Assistant

The Law Assistant is conversational AI based on "КоАП РК" and can answer on any question regarding administrative law.
Current retrieval uses tf-idf + cos siilarity for simplicity of the project. Also considers full-text match.

## Dataset

The dataset used in this project contains information about
law articles, initially taken from here: https://online.zakon.kz/Document/?doc_id=31577399
and adjusted for smaller chunks.

- **Глава:** Chapter number of the law
- **Содержание:** Description of the article
- **Статья:** Artcle number

You can find the data in [`data/data.csv`](data/data.csv).

## Technologies

- Python 3.11
- Docker and Docker Compose for containerization
- [Minsearch](https://github.com/alexeygrigorev/minsearch) for full-text search
- Flask as the API interface (see [Background](#background) for more information on Flask)
- **python-telegram-bot** for Telegram bot integration
- Grafana for monitoring and PostgreSQL as the backend for it
- OpenAI as an LLM

## RAG flow evaluation

For validation dataset I created ground-truth dataset with GPT4-o.

I used the LLM-as-a-Judge metric to evaluate the quality
of the RAG flow.

For `gpt-4o-mini`, in a sample with 200 records, we had:

- 183 (91.5%) `RELEVANT`
- 14(7%) `PARTLY_RELEVANT`
- 3 (1.5%) `NON_RELEVANT`


Also tested `gpt-4o`:

- 185 (92.5%) `RELEVANT`
- 8 (4%) `PARTLY_RELEVANT`
- 7 (3.5%) `NON_RELEVANT`

The difference is minimal, so I opted for `gpt-4o-mini`.

## Preparation

Since we use OpenAI, you need to provide the API key. For the Telegram bot, you also need a Telegram Bot Token.

### API Keys Setup

Edit the `.env` file and add your keys:

```bash
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=your-openai-key-here

# Telegram Bot Token (REQUIRED for Telegram bot)
# Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
```

Alternatively, you can use `direnv`:

1. Install `direnv`. If you use Ubuntu, run `sudo apt install direnv` and then `direnv hook bash >> ~/.bashrc`.
2. Copy `.env` to `.envrc` and insert your keys there.
3. For OpenAI, it's recommended to create a new project and use a separate key.
4. Run `direnv allow` to load the keys into your environment.

For dependency management, we use pipenv, so you need to install it:

```bash
pip install pipenv
```

Once installed, you can install the app dependencies:

```bash
pipenv install --dev
```

## Running the application


### Database configuration

Before the application starts for the first time, the database
needs to be initialized.

First, run `postgres`:

```bash
docker-compose up postgres
```

Then run the [`db_prep.py`](law_assistant/db_prep.py) script:

```bash
pipenv shell

cd law_assistant

export POSTGRES_HOST=localhost
python db_prep.py
```

### Running with Docker-Compose

The easiest way to run the application is with `docker-compose`:

```bash
docker-compose up
```

### Running locally

If you want to run the application locally,
start only postres and grafana:

```bash
docker-compose up postgres grafana
```

If you previously started all applications with
`docker-compose up`, you need to stop the `app`:

```bash
docker-compose stop app
```

Now run the app on your host machine:

```bash
pipenv shell

cd law_assistant

export POSTGRES_HOST=localhost
python app.py
```

## Using the application

When the application is running, we can start using it.

### Telegram Bot 🤖 (NEW!)

The easiest way to interact with the Law Assistant is through **Telegram**!

The Telegram bot allows users to ask questions about Kazakhstan administrative law directly through Telegram messenger. It uses the RAG system to provide accurate answers.

**Quick Start:**

1. Set up your API keys in `.env`:
   ```bash
   OPENAI_API_KEY=your-openai-key
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   ```

2. Install dependencies:
   ```bash
   pipenv install
   ```

3. Run the bot:
   ```bash
   pipenv run python telegram_bot.py
   ```

**Features:**
- Interactive Q&A in Telegram
- Statistics command (`/stats`)
- Bilingual support (Russian/English)
- Optional database logging

📖 **For detailed setup instructions, see [TELEGRAM_BOT_GUIDE.md](TELEGRAM_BOT_GUIDE.md)**

### Terminal Test Script

A simple terminal test script to try the RAG system without setting up the full application:

```bash
pipenv run python terminal_test.py
```

This allows you to test questions directly in your terminal with full statistics.

### CLI

An interactive CLI application was built using
[questionary](https://questionary.readthedocs.io/en/stable/).

To start it, run:

```bash
pipenv run python cli.py
```

You can also make it randomly select a question from
[our ground truth dataset](data/ground-truth-retrieval.csv):

```bash
pipenv run python cli.py --random
```

### Using `requests`

When the application is running, you can use
[requests](https://requests.readthedocs.io/en/latest/)
to send questions—use [test.py](test.py) for testing it:

```bash
pipenv run python test.py
```

It will pick a random question from the ground truth dataset
and send it to the app.

### CURL

You can also use `curl` for interacting with the API:

```bash
URL=http://localhost:5000
QUESTION="Какой штраф есть за пересечение двойной сплошной?"
DATA='{
    "question": "'${QUESTION}'"
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${DATA}" \
    ${URL}/question
```

Sending feedback:

```bash
ID="4e1cef04-bfd9-4a2c-9cdd-2771d8f70e4d"
URL=http://localhost:5000
FEEDBACK_DATA='{
    "conversation_id": "'${ID}'",
    "feedback": 1
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${FEEDBACK_DATA}" \
    ${URL}/feedback
```

After sending it, you'll receive the acknowledgement:

```json
{
    "message": "Feedback received for conversation 4e1cef04-bfd9-4a2c-9cdd-2771d8f70e4d: 1"
}
```

## Monitoring

We use Grafana for monitoring the application. 

It's accessible at [localhost:3000](http://localhost:3000):

- Login: "admin"
- Password: "admin"

### Dashboards

<p align="center">
  <img src="images/dash.png">
</p>

The monitoring dashboard contains several panels:

1. **Last 5 Conversations (Table):** Displays a table showing the five most recent conversations, including details such as the question, answer, relevance, and timestamp. This panel helps monitor recent interactions with users.
2. **+1/-1 (Pie Chart):** A pie chart that visualizes the feedback from users, showing the count of positive (thumbs up) and negative (thumbs down) feedback received. This panel helps track user satisfaction.
3. **Relevancy (Gauge):** A gauge chart representing the relevance of the responses provided during conversations. The chart categorizes relevance and indicates thresholds using different colors to highlight varying levels of response quality.
4. **OpenAI Cost (Time Series):** A time series line chart depicting the cost associated with OpenAI usage over time. This panel helps monitor and analyze the expenditure linked to the AI model's usage.
5. **Tokens (Time Series):** Another time series chart that tracks the number of tokens used in conversations over time. This helps to understand the usage patterns and the volume of data processed.
6. **Model Used (Bar Chart):** A bar chart displaying the count of conversations based on the different models used. This panel provides insights into which AI models are most frequently used.
7. **Response Time (Time Series):** A time series chart showing the response time of conversations over time. This panel is useful for identifying performance issues and ensuring the system's responsiveness.

### Setting up Grafana

All Grafana configurations are in the [`grafana`](grafana/) folder:

- [`init.py`](grafana/init.py) - for initializing the datasource and the dashboard.
- [`dashboard.json`](grafana/dashboard.json) - the actual dashboard (taken from LLM Zoomcamp without changes).

To initialize the dashboard, first ensure Grafana is
running (it starts automatically when you do `docker-compose up`).

Then run:

```bash
pipenv shell

cd grafana

# make sure the POSTGRES_HOST variable is not overwritten 
env | grep POSTGRES_HOST

python init.py
```

Then go to [localhost:3000](http://localhost:3000):

- Login: "admin"
- Password: "admin"

When prompted, keep "admin" as the new password.
