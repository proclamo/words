**Words** is a toy project to play with Ollama and Neo4J from a Jupyter notebook or just from a simple python file.

The idea is to provide a text and the model will extract the words and descriptions from the text. In a later step, it 
will build a Neo4J graph to visualize it. 

I wanted to be able to use all this tools without installing them in my machine, so I've spent time to make it work in Docker.



## Getting started

---

Before setting up all services you should download a [model from Ollama](https://ollama.ai/library):

1. Run Ollama server only
```commandline
    docker compose up llm -d
```
2. Enter to the container
```commandline
    docker compose exec llm sh
```

3. Download the model
```commandline
    ollama pull orca-mini 
```

4. Setup the rest of services
```commandline
    docker compose up
```

5. Got to `http://127.0.0.1:8888` to play with the notebook


## TODO

---

- Improve the prompt to build better graphs
- Try with other models