# neo4j_operations.py
from config import driver
# Fungsi untuk menambahkan individu ke database Neo4j
def add_person_to_neo4j(name, gender):
    with driver.session() as session:
        session.run(
            "MERGE (p:Person {name: $name}) SET p.gender = $gender",
            name=name, gender=gender
        )

# Fungsi untuk menambahkan relasi ke database Neo4j
def add_relation_to_neo4j(person, relation, name, gender=None):
    with driver.session() as session:
        if relation == "Ayah":
            session.run(
                "MERGE (p:Person {name: $person}) "
                "MERGE (f:Person {name: $name}) SET f.gender = 'male' "
                "MERGE (p)-[:HAS_FATHER]->(f) "
                "MERGE (f)-[:HAS_CHILD]->(p)",
                person=person, name=name
            )
        elif relation == "Ibu":
            session.run(
                "MERGE (p:Person {name: $person}) "
                "MERGE (m:Person {name: $name}) SET m.gender = 'female' "
                "MERGE (p)-[:HAS_MOTHER]->(m) "
                "MERGE (m)-[:HAS_CHILD]->(p)",
                person=person, name=name
            )
        elif relation == "Anak":
            session.run(
                "MERGE (p:Person {name: $person}) "
                "MERGE (c:Person {name: $name}) SET c.gender = $gender "
                "MERGE (p)-[:HAS_CHILD]->(c) "
                "MERGE (c)-[:HAS_PARENT]->(p)",
                person=person, name=name, gender=gender
            )
        elif relation in ["Suami", "Istri"]:
            session.run(
                "MERGE (p1:Person {name: $person}) "
                "MERGE (p2:Person {name: $name}) SET p2.gender = $gender "
                "MERGE (p1)-[:HAS_SPOUSE]->(p2) "
                "MERGE (p2)-[:HAS_SPOUSE]->(p1)",
                person=person, name=name, gender=gender
            )
