// === Schema — contraintes d'unicité ===
// L'unicité sur `name` (par label) garantit que les MERGE du seed sont idempotents
// et qu'on ne créera jamais deux nœuds représentant la même entité métier.
// À exécuter UNE FOIS avant le seed.

CREATE CONSTRAINT symptom_name_unique IF NOT EXISTS
FOR (s:Symptom) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT cause_name_unique IF NOT EXISTS
FOR (c:Cause) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT action_name_unique IF NOT EXISTS
FOR (a:Action) REQUIRE a.name IS UNIQUE;
