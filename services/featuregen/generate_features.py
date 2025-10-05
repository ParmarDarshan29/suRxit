"""
Feature generator for suRxit
- For each prescription in DB:
    - compute polypharmacy_count
    - join KG to fetch DDI severity & mechanism
    - allergy match counts
    - food interaction flags
    - produce JSON features and persist to Postgres and Neo4j
"""
import os
import json
import psycopg2
from neo4j import GraphDatabase

# Config
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "surxitpass123")
PG_CONN = os.getenv("PG_CONN", "dbname=sux_db user=suxuser password=suxpass host=localhost")

FEATURE_SCHEMA = [
    "prescription_id", "polypharmacy_count", "high_severity_ddi_count", "moderate_severity_ddi_count",
    "unique_ddi_mechanisms", "allergy_match_count", "food_interaction_flag", "adr_count"
]

def fetch_prescriptions(cur):
    cur.execute("SELECT id, patient_id, drug_ids FROM prescriptions")
    return cur.fetchall()

def compute_features(presc, neo4j_sess):
    prescription_id, patient_id, drug_ids = presc
    drug_list = drug_ids.split(',')
    polypharmacy_count = len(drug_list)
    # DDI severity & mechanism
    ddi_query = """
    UNWIND $drugs AS d1
    UNWIND $drugs AS d2
    WITH d1, d2 WHERE d1 < d2
    MATCH (a:Drug {id: d1})-[r:HAS_DDI]->(b:Drug {id: d2})
    RETURN r.severity AS severity, r.mechanism AS mechanism
    """
    ddi_res = neo4j_sess.run(ddi_query, drugs=drug_list)
    high_sev, mod_sev, mechanisms = 0, 0, set()
    for row in ddi_res:
        if row["severity"] == "high":
            high_sev += 1
        elif row["severity"] == "moderate":
            mod_sev += 1
        if row["mechanism"]:
            mechanisms.add(row["mechanism"])
    # Allergy match
    allergy_query = """
    MATCH (p:Patient {id: $pid})-[:HAS_ALLERGY]->(a:Allergy)
    RETURN count(DISTINCT a) AS allergy_matches
    """
    allergy_res = neo4j_sess.run(allergy_query, pid=patient_id)
    allergy_match_count = allergy_res.single()[0]
    # Food interaction
    food_query = """
    MATCH (d:Drug)-[r:HAS_DFI]->(f:Food)
    WHERE d.id IN $drugs
    RETURN count(DISTINCT f) > 0 AS food_flag
    """
    food_res = neo4j_sess.run(food_query, drugs=drug_list)
    food_flag = bool(food_res.single()[0])
    # ADR count
    adr_query = """
    MATCH (d:Drug)-[:HAS_ADR]->(s:SideEffect)
    WHERE d.id IN $drugs
    RETURN count(DISTINCT s) AS adr_count
    """
    adr_res = neo4j_sess.run(adr_query, drugs=drug_list)
    adr_count = adr_res.single()[0]
    return {
        "prescription_id": prescription_id,
        "polypharmacy_count": polypharmacy_count,
        "high_severity_ddi_count": high_sev,
        "moderate_severity_ddi_count": mod_sev,
        "unique_ddi_mechanisms": list(mechanisms),
        "allergy_match_count": allergy_match_count,
        "food_interaction_flag": food_flag,
        "adr_count": adr_count
    }

def persist_features_pg(cur, features):
    cur.execute(
        """
        INSERT INTO prescription_features (prescription_id, features)
        VALUES (%s, %s)
        ON CONFLICT (prescription_id) DO UPDATE SET features = EXCLUDED.features
        """,
        (features["prescription_id"], json.dumps(features))
    )

def persist_features_neo4j(sess, features):
    sess.run(
        """
        MATCH (p:Prescription {id: $pid})
        SET p.features = $features
        """,
        pid=features["prescription_id"], features=json.dumps(features)
    )

def main():
    pg_conn = psycopg2.connect(PG_CONN)
    pg_cur = pg_conn.cursor()
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    with neo4j_driver.session() as neo4j_sess:
        prescriptions = fetch_prescriptions(pg_cur)
        for presc in prescriptions:
            features = compute_features(presc, neo4j_sess)
            persist_features_pg(pg_cur, features)
            persist_features_neo4j(neo4j_sess, features)
            print(f"Features for prescription {features['prescription_id']}: {features}")
    pg_conn.commit()
    pg_cur.close()
    pg_conn.close()
    neo4j_driver.close()

if __name__ == "__main__":
    main()
