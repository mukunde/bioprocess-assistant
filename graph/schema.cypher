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

// Full-text index on Symptom (name + description + keywords).
// 'french' analyzer: stemming + French stop-word removal so queries like
// "rendement faible" or "perte rendement" match the node
// "Chute du rendement de capture" without requiring exact phrasing.
// The `keywords` field holds curated FR/EN synonyms to boost recall on
// paraphrases (e.g. "surpression", "HMW", "protéines de cellule hôte") - added
// after the evaluation suite (eval/) revealed recall gaps at threshold 2.5.
// DROP first: a fulltext index definition cannot be updated in place
// (CREATE ... IF NOT EXISTS is a no-op when the index already exists).
DROP INDEX symptom_text IF EXISTS;
CREATE FULLTEXT INDEX symptom_text IF NOT EXISTS
FOR (s:Symptom) ON EACH [s.name, s.description, s.keywords]
OPTIONS {indexConfig: {`fulltext.analyzer`: 'french'}};
