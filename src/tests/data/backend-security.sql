INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 'PASSIVETEST01', 'EUR', (SELECT id FROM last_rate WHERE fund_id = 123), 'FI0000000','Passive test fund 1 - fi', 'Passive test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 'ACTIVETEST01', 'EUR', (SELECT id FROM last_rate WHERE fund_id = 234), 'FI0000000','Active test fund 1 - fi', 'Active test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 'BALANCEDTEST01', 'EUR', (SELECT id FROM last_rate WHERE fund_id = 345), 'FI0000000','Balanced test fund 1 - fi', 'Balanced test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 'FIXEDTEST01', 'EUR', (SELECT id FROM last_rate WHERE fund_id = 456), 'Fixed test fund 1 - fi', 'Fixed test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 'DIMETEST01', 'EUR', (SELECT id FROM last_rate WHERE fund_id = 678), 'Dimensional test fund 1 - fi', 'Dimensional test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 'SPILTANTEST', 'SEK', (SELECT id FROM last_rate WHERE fund_id = 789), 'EUR','FI0000000','Spiltan test fund 1 - fi', 'Spiltan test fund 1 - en');

