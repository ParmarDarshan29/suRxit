# Neo4j Cypher Constraints for MedKG-Rx

-- Node Uniqueness Constraints
CREATE CONSTRAINT unique_drug_id IF NOT EXISTS FOR (d:Drug) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT unique_sideeffect_id IF NOT EXISTS FOR (s:SideEffect) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT unique_allergy_id IF NOT EXISTS FOR (a:Allergy) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT unique_food_id IF NOT EXISTS FOR (f:Food) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT unique_patient_id IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE;

-- Indexes for Query Performance
CREATE INDEX drug_name_idx IF NOT EXISTS FOR (d:Drug) ON (d.name);
CREATE INDEX sideeffect_name_idx IF NOT EXISTS FOR (s:SideEffect) ON (s.name);
CREATE INDEX allergy_name_idx IF NOT EXISTS FOR (a:Allergy) ON (a.name);
CREATE INDEX food_name_idx IF NOT EXISTS FOR (f:Food) ON (f.name);
CREATE INDEX patient_name_idx IF NOT EXISTS FOR (p:Patient) ON (p.name);

-- Relationship Properties (no constraints, but properties are as defined in CSVs)
-- Example: (Drug)-[:INTERACTS_WITH {severity, mechanism, evidence, confidence}]-(Drug)
