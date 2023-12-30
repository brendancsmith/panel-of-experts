# Panel of Experts

10 stochastic parrots are better than 1 🦜

This is a small chatbot app using the OpenAI API through LangChain and the Chainlit web interface. It queries OpenAI multiple times in parallel and then produces a consensus answer.

Inspired by the concept of "wisdom of the crowd", it is a proof-of-concept in addressing the inconsistency of responses from LLMs (a.k.a. stochastic parrots). After starting this project, I learned that this is essentially a simple implementation of Self-consistency Sampling [Wang et al. 2022a](https://arxiv.org/abs/2203.11171).

## Demo

In the March 1964 issue of Scientific American, mathematician [Martin Gardner](https://en.wikipedia.org/wiki/Martin_Gardner) published a math puzzle that ChatGPT is ill-equipped to solve without much more instruction:

>Using each of the nine digits once, and only once, form a set of three primes that have the lowest possible sum. For example, the set 941, 827 and 653 sum to 2,421, but this is far from minimal.

Interestingly, with this simple sampling technique, the "moderator" of the panel is able to solve this math puzzle even when none of the "experts" can. By using the expert responses as context, it is able to evaluate many different approaches to solving the puzzle and reason much more effectively about the correct approach to the solution. By comparison, ChatGPT 4 with the Code Interpreter feature enabled is routinely unable to solve this puzzle, despite it being programmatically trivial.

The result is shown [here](demo/gardner.png).

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

## Usage

```bash
chainlit run app.py -w
```

## Notes

- Developed and tested with Python 3.11.6
