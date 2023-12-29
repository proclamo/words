FROM ollama/ollama

ARG MODEL

RUN ollama serve

RUN ollama pull ${MODEL}

EXPOSE 11434