# config.py
from neo4j import GraphDatabase

# Koneksi ke database Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"
driver = GraphDatabase.driver(uri, auth=(username, password))