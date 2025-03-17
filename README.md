# Mini RAG App

This is a minimal implementation of the RAG model for question answering.

## Requirements

- Python 3.8 or later

### Install python using Miniconda

1) Download and install Miniconda from [here](https://www.anaconda.com/docs/main#quick-command-line-install)

2) Create a new enviroment using the following command:
```bash
$ conda create -n mini-rag-app python=3.8
```

3) Activate the enviroment:
```bash
$ conda activate mini-rag-app
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the enviroment variables

```bash
$ cp env.example .env
```

set your enviroment variable in the `.env` file. Like `OPENAI_API_KEY` value.