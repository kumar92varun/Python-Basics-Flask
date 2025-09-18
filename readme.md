## Installation Instructions

### Set up a Python Virtual Environment

```bash
python3.12 -m venv .environment
```

### Activate the Virtual Environment

```bash
source .environment/bin/activate
```


### Installing all Python packages

```bash
pip install -r requirements.txt
```


### Create a `.env` file

```bash
cp .env.example .env
```

### Configure values in `.env` file


## Running the application locally

### Serve the application using Flask

```bash
flask run --debug
```