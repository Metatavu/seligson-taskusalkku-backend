INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), 14.116300);
INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), 88.046300);
INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), 12.274700);
INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), 9.971300);
INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'DIMETEST01'), 1313.410000);
INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'SPILTAN TEST'), 39.209700);

INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'EUR'), 12345.12345);
INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'FIM'), 2345.2345);
INSERT INTO last_rate (id, security_id, rate_close) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), (SELECT id FROM security WHERE original_id = 'SEK'), 345.345);