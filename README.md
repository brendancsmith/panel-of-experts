# Panel of Experts

10 stochastic parrots are better than 1 🦜

This is a simple chatbot app using Chainlit and LangChain which queries OpenAI in parallel and then produces a consensus answer.

## Setup

### OpenAI API Key

Get an [OpenAI API Key](https://platform.openai.com/account/api-keys) and set the environment variable `OPENAI_API_KEY` on your system (`export OPENAI_API_KEY="your key here"`). Ideally, you should set this in your `.bashrc` or `.zshrc` file since many other OpenAI projects (including the official API clients) use this environment variable.

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configuration

Settings in `config.toml`:
- Recommended to change the model from `gpt-3.5-turbo` to `gpt-4-1106-preview` for better results.
- Change the number of `experts` if desired (default 10).

## Usage

```bash
chainlit run app.py -w
```

## Notes

- Developed and tested on Python 3.11.6
