# Panel of Experts

A chatbot app using Chainlit and LangChain which queries OpenAI multiple times and then produces a consensus answer.

## Setup

### OpenAI API Key

Get an [OpenAI API Key](https://platform.openai.com/account/api-keys) and set the environment variable `OPENAI_API_KEY` on your system (`export OPENAI_API_KEY="your key here"`). Ideally, you should set this in your `.bashrc` or `.zshrc` file since many other OpenAI projects (including the official API clients) use this environment variable.

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Documents

Place your documents in the `data` directory. Many different formats are supported by LlamaIndex. See the [LlamaIndex documentation](https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader.html#supported-file-types) for a complete list.

## Usage

```bash
chainlit run app.py -w
```

## Notes

- Developed and tested on Python 3.11.6
