CREATE TABLE IF NOT EXISTS tax_havens(
  code TEXT PRIMARY KEY
);
INSERT INTO tax_havens(code) VALUES
('VG'), -- Îles Vierges britanniques
('KY'), -- Îles Caïmans
('BM'), -- Bermudes
('NL'), -- Pays-Bas
('CH'), -- Suisse
('LU'), -- Luxembourg
('HK'), -- Hong-Kong
('JE'), -- Jersey
('SG'), -- Singapour
('AE')  -- Émirats Arabes Unis
ON CONFLICT DO NOTHING;
