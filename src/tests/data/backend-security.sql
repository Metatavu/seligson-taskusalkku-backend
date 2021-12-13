INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE("9BED2C6F-8F2C-4E6D-A711-D75CB2474616", "-",""))), 'PASSIVETEST01', 'EUR', (SELECT id FROM fund WHERE original_id = 123), 'Passive test fund 1 - fi', 'Passive test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE("D84DFB1A-3230-4D0E-ABCB-2A9F9B118AFA", "-",""))), 'ACTIVETEST01', 'EUR', (SELECT id FROM fund WHERE original_id = 234), 'Active test fund 1 - fi', 'Active test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE("87C526DF-C4B0-42D2-8202-07C990C725DB", "-",""))), 'BALANCEDTEST01', 'EUR', (SELECT id FROM fund WHERE original_id = 345), 'Balanced test fund 1 - fi', 'Balanced test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE("A2C14970-161B-407A-9961-D1B14739EC2A", "-",""))), 'FIXEDTEST01', 'EUR', (SELECT id FROM fund WHERE original_id = 456), 'Fixed test fund 1 - fi', 'Fixed test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE("49D73D12-3061-469A-BA67-0B4A906DD4FC", "-",""))), 'DIMETEST01', 'EUR', (SELECT id FROM fund WHERE original_id = 678), 'Dimensional test fund 1 - fi', 'Dimensional test fund 1 - en');
INSERT INTO security (id, original_id, currency, fund_id, name_fi, name_sv) VALUES ((UNHEX(REPLACE("B01F0D42-E133-44F1-A3C2-D0B560B868AE", "-",""))), 'SPILTAN TEST', 'SEK', (SELECT id FROM fund WHERE original_id = 789),'Spiltan test fund 1 - fi', 'Spiltan test fund 1 - en');
INSERT INTO security (id, original_id, currency, name_fi, name_sv) VALUES ((UNHEX(REPLACE("F8C7FE3A-8F95-4D93-AB6D-DF0165CA8D5A", "-",""))), 'EUR', 'EUR', 'Ecu', 'Ecu');
INSERT INTO security (id, original_id, currency, name_fi, name_sv) VALUES ((UNHEX(REPLACE("7A20D26F-DC4E-45E9-90A6-67904FC7BE35", "-",""))),'FIM', 'EUR', 'Suomen markka', 'Finska mark');
INSERT INTO security (id, original_id, currency, name_fi, name_sv) VALUES ((UNHEX(REPLACE("23F2428E-4D90-4867-8CDF-557672944115", "-",""))),'SEK', 'EUR', 'Ruotsin, kruunu', 'Ruotsin, kruunu');