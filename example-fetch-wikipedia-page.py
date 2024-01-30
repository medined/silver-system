#!/usr/bin/env python

#
# https://github.com/tomasonjo/blogs/blob/master/llm/neo4jvector_langchain_deepdive.ipynb
#

from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_community.document_loaders import WikipediaLoader
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

from dotenv import load_dotenv
import os

load_dotenv()

database = os.getenv("NEO4J_DATABASE", default="neo4j")

# Read the wikipedia article
raw_documents = WikipediaLoader(query="The Witcher").load()
# Define chunking strategy
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000, chunk_overlap=20
)
# Chunk the document
documents = text_splitter.split_documents(raw_documents)
# Remove the summary
for d in documents:
    del d.metadata["summary"]

neo4j_db = Neo4jVector.from_documents(
    documents,
    OpenAIEmbeddings(),
    database=database,
    index_name="wikipedia",
    node_label="WikipediaArticle",
    text_node_property="info",
    embedding_node_property="vector",
    create_id_index=True,
    pre_delete_collection=True,
)

print(neo4j_db.query("SHOW CONSTRAINTS"))
#[{'id': 4,
#  'name': 'constraint_e5da4d45',
#  'type': 'UNIQUENESS',
#  'entityType': 'NODE',
#  'labelsOrTypes': ['WikipediaArticle'],
#  'properties': ['id'],
#  'ownedIndex': 'constraint_e5da4d45',
#  'propertyType': None}]

print(neo4j_db.query(
    """SHOW INDEXES
       YIELD name, type, labelsOrTypes, properties, options
       WHERE type = 'VECTOR'
    """
))
#[{'name': 'wikipedia',
#  'type': 'VECTOR',
#  'labelsOrTypes': ['WikipediaArticle'],
#  'properties': ['vector'],
#  'options': {'indexProvider': 'vector-1.0',
#   'indexConfig': {'vector.dimensions': 1536,
#    'vector.similarity_function': 'cosine'}}}]

neo4j_db.add_documents(
    [
        Document(
            page_content="LangChain is the coolest library since the Library of Alexandria",
            metadata={"author": "Tomaz", "confidence": 1.0}
        )
    ],
    ids=["langchain"],
)

#
# load from existing Neo4j index
#
# existing_index = Neo4jVector.from_existing_index(
#     OpenAIEmbeddings(),
#     url=url,
#     username=username,
#     password=password,
#     index_name="wikipedia",
#     text_node_property="info",  # Need to define if it is not default
# )
# print(existing_index.node_label)
# print(existing_index.embedding_node_property)

# existing_index.query(
#     """MATCH (w:WikipediaArticle {id:'langchain'})
#        MERGE (w)<-[:EDITED_BY]-(:Person {name:"Galileo"})
#     """
# )

# read_query = (
#     "CALL db.index.vector.queryNodes($index, $k, $embedding) "
#     "YIELD node, score "
# ) + retrieval_query

# retrieval_query = """
# OPTIONAL MATCH (node)<-[:EDITED_BY]-(p)
# WITH node, score, collect(p) AS editors
# RETURN node.info AS text,
#        score,
#        node {.*, vector: Null, info: Null, editors: editors} AS metadata
# """

# existing_index_return = Neo4jVector.from_existing_index(
#     OpenAIEmbeddings(),
#     url=url,
#     username=username,
#     password=password,
#     database="neo4j",
#     index_name="wikipedia",
#     text_node_property="info",
#     retrieval_query=retrieval_query,
# )

# existing_index_return.similarity_search("What do you know about LangChain?", k=1)