# Gitlab Burndown

This tool generates a burndown chart for a Gitlab project. It uses the Gitlab
API to fetch the issues and their estimated time.
The current implementation does not consider the time spent on the issues.

## Installation

It is required to install `poetry`, `git` and `make` to use this tool currently.

```bash
git clone git://github.com/bespinian/gitlab-burndown.git
cd gitlab-burndown
make install
```

## Usage

Copy the `.env.example` file to `.env` and fill in the required values.

```bash
cp .env.example .env
```

Run the following command to generate the burndown chart (`burndown_chart.png`).

```bash
poetry run python main.py 1m

# To see the help message
poetry run python main.py --help
```

## Development

To run the tests, run the following command.

```bash
make test
```

To run the formatter and linter, run the following command.

```bash
make format
```
