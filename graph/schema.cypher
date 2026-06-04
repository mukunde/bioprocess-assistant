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
// 'english' analyzer: stemming + English stop-word removal. The graph content is
// English (the source handbooks are English); French user questions are bridged
// to English at retrieval time. The `keywords` field holds curated discriminative
// EN synonyms to boost recall on paraphrases (e.g. "overpressure", "HMW") - added
// after the evaluation suite (eval/) revealed recall gaps.
// DROP first: a fulltext index definition cannot be updated in place
// (CREATE ... IF NOT EXISTS is a no-op when the index already exists).
DROP INDEX symptom_text IF EXISTS;
CREATE FULLTEXT INDEX symptom_text IF NOT EXISTS
FOR (s:Symptom) ON EACH [s.name, s.description, s.keywords]
OPTIONS {indexConfig: {`fulltext.analyzer`: 'english'}};
