"""
Neo4j import script for suRxit KG
- Reads all manual CSVs
- Creates constraints & indexes
- Imports nodes & relationships
- Logs stats (node/rel counts)
"""
import os
import glob
import csv
from neo4j import GraphDatabase

# Config
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "surxitpass123")
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/manual'))

# Node and relationship CSVs
NODE_FILES = [
    ("Allergy", "nodes_allergy.csv"),
    ("Drug", "nodes_drug.csv"),
    ("Food", "nodes_food.csv"),
    ("Patient", "nodes_patient.csv"),
    ("SideEffect", "nodes_sideeffect.csv"),
]
REL_FILES = [
    ("HAS_ADR", "rels_adr.csv"),
    ("HAS_DDI", "rels_ddi.csv"),
    ("HAS_DFI", "rels_dfi.csv"),
    ("HAS_ALLERGY", "rels_allergy.csv"),
]

# Cypher for constraints/indexes
CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Drug) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Allergy) REQUIRE a.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Food) REQUIRE f.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:SideEffect) REQUIRE s.id IS UNIQUE",
]


def import_nodes(tx, label, csv_path):
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            props = {k: v for k, v in row.items() if v != ''}
            cypher = f"MERGE (n:{label} {{id: $id}}) SET n += $props"
            tx.run(cypher, id=props['id'], props=props)

def import_rels(tx, rel_type, csv_path):
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Determine start/end columns based on rel_type or file
            if rel_type == "HAS_ADR":
                start_id = row['drug_id']
                end_id = row['sideeffect_id']
                exclude = ['drug_id', 'sideeffect_id']
            elif rel_type == "HAS_DFI":
                start_id = row['drug_id']
                end_id = row['food_id']
                exclude = ['drug_id', 'food_id']
            elif rel_type == "HAS_ALLERGY":
                start_id = row['patient_id']
                end_id = row['allergy_id']
                exclude = ['patient_id', 'allergy_id']
            else:  # HAS_DDI
                start_id = row['start_id']
                end_id = row['end_id']
                exclude = ['start_id', 'end_id']
            props = {k: v for k, v in row.items() if k not in exclude and v != ''}
            cypher = (
                f"MATCH (a {{id: $start_id}}) MATCH (b {{id: $end_id}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) SET r += $props"
            )
            tx.run(cypher, start_id=start_id, end_id=end_id, props=props)

def log_stats(driver):
    with driver.session() as session:
        node_count = session.run("MATCH (n) RETURN count(n)").single()[0]
        rel_count = session.run("MATCH ()-[r]->() RETURN count(r)").single()[0]
        print(f"Total nodes: {node_count}")
        print(f"Total relationships: {rel_count}")

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    with driver.session() as session:
        print("Creating constraints...")
        for c in CONSTRAINTS:
            session.run(c)
        print("Importing nodes...")
        for label, fname in NODE_FILES:
            path = os.path.join(DATA_DIR, fname)
            print(f"  {label}: {fname}")
            session.execute_write(import_nodes, label, path)
        print("Importing relationships...")
        for rel_type, fname in REL_FILES:
            path = os.path.join(DATA_DIR, fname)
            print(f"  {rel_type}: {fname}")
            session.execute_write(import_rels, rel_type, path)
        print("Logging stats...")
        log_stats(driver)
    driver.close()

if __name__ == "__main__":
    main()
