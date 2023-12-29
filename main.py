import os
import json

from langchain.chat_models import ChatOllama
from langchain.schema import StrOutputParser
from langchain.prompts import PromptTemplate
from neo4j import GraphDatabase

model_uri = os.environ.get("MODEL_URI")
neo4j_uri = os.environ.get("NEO4J_URI")

template = """
    You are a graph builder. You are provided with a text. The text will be full of descriptions of persons and objects.
    You have to extract the keyword, the property and the relation between them. 
    You have to build the graph following the next json structure:

    ```
    [
        {{
            "node1": keyword1,
            "node2": description,
            "edge": relation
        }},
        {{ ... }}
        ...
    ]
    ```

    Notes:
        - the relation uses to be the verb (i.e.: "The house is red" -> node1: 'house', node2: 'red', 'edge': 'is' )
        - sometimes the relation is implicit: (i.e.: "A blue shirt" -> node1: 'shirt', node2: 'blue', 'edge': 'is')
        - if there are more than one property, you'll make several entries in the json
        - make the graph with all the sentences and words of the provided text
        - the response must be a valid JSON array of objects


    Text: {text}
    """

model = ChatOllama(base_url=model_uri, model="orca-mini", temperature=0)
prompt = PromptTemplate.from_template(template)
output_parser = StrOutputParser()

chain = prompt | model | output_parser

input = """ 
In a small, bustling town, the clock at the train station struck 13 hours. The sun shone brightly, casting a warm, golden glow on the scene. The station, an old but well-maintained structure, bore the classic charm of early 20th-century architecture. Its red brick walls, adorned with ivy, exuded a sense of history and permanence.
People of various walks of life milled about, each absorbed in their own world. A young family stood near the entrance: a mother, father, and two children. The father, dressed in a simple, neatly pressed cotton shirt and denim jeans, held a small suitcase, his eyes scanning the train schedule. The mother, beside him, wore a floral dress made of light fabric, perfect for the warm day, and held the hand of their youngest, a girl of about five, in a pink sundress and white sandals. Their son, perhaps eight, stood a bit apart, his curiosity piqued by the surroundings, dressed in shorts and a striped T-shirt.
Nearby, a group of friends, probably in their late teens, chatted animatedly. They were a diverse bunch. One girl, with long, curly hair, wore a vibrant red top and black jeans, her style striking and confident. Another, shorter and with straight hair, had on a pastel-colored T-shirt and shorts, her demeanor more reserved. Among the boys, one sported a sports jersey and shorts, clearly a fan of some local team, while another wore a simple polo shirt and khaki pants. Their laughter and chatter added a lively energy to the atmosphere.
On a bench, an elderly couple sat quietly, enjoying the warmth of the day. The man, with wisps of white hair and a kind face, wore a light sweater despite the warmth, and trousers that spoke of a different era. His companion, a woman of similar age, had her hair neatly tied in a bun, and wore a classic dress, its floral pattern faded but elegant. They shared a serene, contented silence, occasionally exchanging soft words.
The station itself was a marvel. Its high ceiling was supported by sturdy wooden beams, and the large windows let in ample natural light. The benches were of simple, solid wood, polished by years of use. The departure board, a mix of digital and old mechanical styles, clicked and whirred as train times updated.
On the platform, a businessman stood apart, his posture tense. Dressed in a sharp suit, his attention was fixed on his phone, the modern world intruding upon this timeless scene. His briefcase, a sleek, modern design, contrasted with the rustic charm of the station.
A vendor, with a small cart filled with snacks and drinks, moved through the crowd. His attire was casual, a T-shirt and jeans, and his warm smile invited conversation. People occasionally stopped him, buying a quick snack or a bottle of water, exchanging pleasantries.
"""

response = chain.invoke({"text": input})

# the response never comes as valid JSON, so here I manipulate it

r = "},{".join(response.split("""}

        {"""))

data = f"[{r}]"
graph = json.loads(data)

def insert_nodes(tx, n):
    result = tx.run(
        """
        CREATE (:Word { value: $node1 })-[:IS { relation: $edge }]->(:Word { value: $node2 })
        """,
        node1=n.get("node1"),
        node2=n.get("node2"),
        edge=n.get("edge")
    )
    return result


with GraphDatabase.driver(uri=neo4j_uri, auth=None) as driver:
    with driver.session(database="neo4j") as session:
        for n in graph:
            result = session.execute_write(insert_nodes, n)
            print(result)