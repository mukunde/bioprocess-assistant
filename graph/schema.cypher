// === Schema - uniqueness constraints ===
// Uniqueness on `name` (per label) keeps the seed's MERGE operations idempotent
// and prevents duplicate nodes representing the same domain entity.
// Run once before the seed.

CREATE CONSTRAINT symptom_name_unique IF NOT EXISTS
FOR (s:Symptom) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT cause_name_unique IF NOT EXISTS
FOR (c:Cause) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT action_name_unique IF NOT EXISTS
FOR (a:Action) REQUIRE a.name IS UNIQUE;

// Full-text index on Symptom (name + description).
// 'french' analyzer: stemming + French stop-word removal so queries like
// "rendement faible" or "perte rendement" match the node
// "Chute du rendement de capture" without requiring exact phrasing.
CREATE FULLTEXT INDEX symptom_text IF NOT EXISTS
FOR (s:Symptom) ON EACH [s.name, s.description]
OPTIONS {indexConfig: {`fulltext.analyzer`: 'french'}};
