#!/bin/bash
# Import bridges k95-k130 from CSV to database

sqlite3 db/kh.db << 'EOF'
-- Import k95
INSERT OR REPLACE INTO keys (puzzle_id, priv_hex, wif, found_range_start_hex, found_range_end_hex, source, ts)
VALUES (95, '527a792b183c7f64a0e8b1f4', '5HpHagT65TZzG1PH3CSu63k8DbpvDK3oLkXopFWYcRf7mQi3DKr', '400000000000000000000000', '7fffffffffffffffffffffff', 'CSV import', datetime('now'));

-- Import k100
INSERT OR REPLACE INTO keys (puzzle_id, priv_hex, wif, found_range_start_hex, found_range_end_hex, source, ts)
VALUES (100, 'af55fc59c335c8ec67ed24826', '5HpHagT65TZzG1PH3CSu63k8DbpvK7HR71pmCJKRum9ySBN3fA4', '8000000000000000000000000', 'fffffffffffffffffffffffff', 'CSV import', datetime('now'));

-- Import k105
INSERT OR REPLACE INTO keys (puzzle_id, priv_hex, wif, found_range_start_hex, found_range_end_hex, source, ts)
VALUES (105, '16f14fc2054cd87ee6396b33df3', '5HpHagT65TZzG1PH3CSu63k8DbpyfD3oPVBrwMG66gs4W77dCDN', '100000000000000000000000000', '1ffffffffffffffffffffffffff', 'CSV import', datetime('now'));

-- Import k110
INSERT OR REPLACE INTO keys (puzzle_id, priv_hex, wif, found_range_start_hex, found_range_end_hex, source, ts)
VALUES (110, '35c0d7234df7deb0f20cf7062444', '5HpHagT65TZzG1PH3CSu63k8Dbs9XGA3SYCnJzwvqRrMP9SpvPd', '2000000000000000000000000000', '3fffffffffffffffffffffffffff', 'CSV import', datetime('now'));

-- Import k115
INSERT OR REPLACE INTO keys (puzzle_id, priv_hex, wif, found_range_start_hex, found_range_end_hex, source, ts)
VALUES (115, '60f4d11574f5deee49961d9609ac6', '5HpHagT65TZzG1PH3CSu63k8DcwG8A3B7LtEGDMyTJEvhXBWr4G', '40000000000000000000000000000', '7ffffffffffffffffffffffffffff', 'CSV import', datetime('now'));

-- Import k120
INSERT OR REPLACE INTO keys (puzzle_id, priv_hex, wif, found_range_start_hex, found_range_end_hex, source, ts)
VALUES (120, 'b10f22572c497a836ea187f2e1fc23', '5HpHagT65TZzG1PH3CSu63k8EAExDJA7fR4CiwcHHf9V14DiNUC', '800000000000000000000000000000', 'ffffffffffffffffffffffffffffff', 'CSV import', datetime('now'));

-- Import k125
INSERT OR REPLACE INTO keys (puzzle_id, priv_hex, wif, found_range_start_hex, found_range_end_hex, source, ts)
VALUES (125, '1c533b6bb7f0804e09960225e44877ac', '5HpHagT65TZzG1PH3CSu63k8cVKMSzAfNoXxFHk12Dsw2LJTDMY', '10000000000000000000000000000000', '1fffffffffffffffffffffffffffffff', 'CSV import', datetime('now'));

-- Import k130
INSERT OR REPLACE INTO keys (puzzle_id, priv_hex, wif, found_range_start_hex, found_range_end_hex, source, ts)
VALUES (130, '33e7665705359f04f28b88cf897c603c9', '5HpHagT65TZzG1PH3CSu63kKneRgm8KMsKMXHv9N2Wx29e92a7b', '200000000000000000000000000000000', '3ffffffffffffffffffffffffffffffff', 'CSV import', datetime('now'));

-- Verify imports
SELECT COUNT(*) as imported FROM keys WHERE puzzle_id >= 95 AND puzzle_id <= 130;
SELECT puzzle_id FROM keys WHERE puzzle_id >= 95 AND puzzle_id <= 130 ORDER BY puzzle_id;
EOF

echo "✅ Bridges k95-k130 imported successfully!"
