INSERT INTO portfolio (id, original_id, company_id) VALUES ((UNHEX(REPLACE("6bb05ba3-2b4f-4031-960f-0f20d5244440", "-",""))), '123', (SELECT id FROM company WHERE original_id = '123'));
INSERT INTO portfolio (id, original_id, company_id) VALUES ((UNHEX(REPLACE("84da0adf-db11-4be9-8c51-fcebc05a1d4f", "-",""))), '123_2', (SELECT id FROM company WHERE original_id = '123'));
INSERT INTO portfolio (id, original_id, company_id) VALUES ((UNHEX(REPLACE("ba4869f3-dff4-409f-9208-69503f88f228", "-",""))), '124', (SELECT id FROM company WHERE original_id = '124'));
INSERT INTO portfolio (id, original_id, company_id) VALUES ((UNHEX(REPLACE("10b9cf58-669a-492a-9fb4-91e18129916d", "-",""))), '125', (SELECT id FROM company WHERE original_id = '125'));
INSERT INTO portfolio (id, original_id, company_id) VALUES ((UNHEX(REPLACE("c510d0a5-78bf-454d-af64-75587e9cc315", "-",""))), '126', (SELECT id FROM company WHERE original_id = '126'));
