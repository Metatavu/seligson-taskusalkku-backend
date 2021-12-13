INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 1, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-01-23', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 2, (SELECT id FROM portfolio WHERE original_id = '123'), '12', '1998-01-23', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 3, (SELECT id FROM portfolio WHERE original_id = '123'), '80', '1998-01-23', 5000.00, (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), null, 3.5, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 4, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-01-26', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 5, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-01-27', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 6, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-01-28', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 7, (SELECT id FROM portfolio WHERE original_id = '123'), '12', '1998-02-01', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 8, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-02-10', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 9, (SELECT id FROM portfolio WHERE original_id = '123'), '12', '1998-02-11', 10099.17, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 10, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-02-12', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 11, (SELECT id FROM portfolio WHERE original_id = '123'), '12', '1998-02-13', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 12, (SELECT id FROM portfolio WHERE original_id = '123'), '12', '1998-02-14', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 13, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-03-23', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 14, (SELECT id FROM portfolio WHERE original_id = '123'), '12', '1998-04-23', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 15, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-05-23', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 16, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-05-24', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 17, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-05-25', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 18, (SELECT id FROM portfolio WHERE original_id = '123'), '80', '1998-06-26', 0.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 19, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-07-27', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 20, (SELECT id FROM portfolio WHERE original_id = '123'), '12', '1998-07-28', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 21, (SELECT id FROM portfolio WHERE original_id = '123'), '11', '1998-07-28', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 22, (SELECT id FROM portfolio WHERE original_id = '123'), '12', '1998-07-28', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 23, (SELECT id FROM portfolio WHERE original_id = '123_2'), '11', '1998-07-28', 5000.0, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0); ;
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 24, (SELECT id FROM portfolio WHERE original_id = '123_2'), '11', '1998-08-02', 5000.0, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0); ;
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 25, (SELECT id FROM portfolio WHERE original_id = '123_2'), '12', '1998-08-03', 41.47, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 26, (SELECT id FROM portfolio WHERE original_id = '123_2'), '11', '1998-08-04', 12.45, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 27, (SELECT id FROM portfolio WHERE original_id = '125'), '11', '1998-09-10', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 28, (SELECT id FROM portfolio WHERE original_id = '125'), '12', '1998-09-11', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 29, (SELECT id FROM portfolio WHERE original_id = '126'), '11', '1998-09-12', 10147.38, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status) VALUES ((UNHEX(REPLACE(UUID(), "-",""))), 30, (SELECT id FROM portfolio WHERE original_id = '126'), '12', '1998-10-11', 5000.00, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 30, 28, DATE('1998-01-21'), 10, 0, 0);

INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('813230f0-7c0b-4988-8ef8-9fc9907f4edf', "-",""))), 100, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-01'), 10, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 8.891322479445751, 46.69736344844192, DATE('2020-05-29'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('a5b5da2f-588c-4ef9-b21d-813fd6a541ef', "-",""))), 200, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-01'), 10, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 46.54840931204268, 16.855289578264443, DATE('2020-05-29'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('350a9515-3ff8-4c1d-aa69-f0e53ed60aee', "-",""))), 300, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-01'), 0, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), 35.19015936647667, 35.371359239195854, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('2c4f9f81-6402-4ab9-b563-d0f7b8f16493', "-",""))), 101, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-02'), 20, (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), null, 47.079324355428255, 2.6873307724862294, DATE('2020-05-30'), 19.96, 0.04, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('04eda117-fe8b-4094-a00b-a6323b442cd5', "-",""))), 201, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-02'), 20, (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), null, 28.265901944659, 15.118669347692105, DATE('2020-05-30'), 19.96, 0.04, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('772316ca-46d9-4501-bb4b-189b287a0bf5', "-",""))), 301, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-02'), 0, (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), 13.231340759194666, 32.56782685435009, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('1de01320-1b5b-4e72-b4e0-785a98d40739', "-",""))), 102, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-03'), 30, (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), null, 48.50194522494567, 41.719267038694305, DATE('2020-05-31'), 29.94, 0.06, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('bd58f793-00ab-4ad3-804f-fb1cc7a885be', "-",""))), 202, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-03'), 30, (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), null, 25.144628748577922, 2.3611685538669325, DATE('2020-05-31'), 29.94, 0.06, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('4cfdc2bb-ec9d-4fa7-992e-70c3e9f42a3e', "-",""))), 302, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-03'), 0, (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), 33.60721545128838, 0.1861013694734459, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('27062691-7f69-4f18-b96f-10e5097ef90d', "-",""))), 103, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-04'), 40, (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), null, 38.957854629988596, 9.454822352361536, DATE('2020-06-01'), 39.92, 0.08, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('4cfa2d60-aa95-46a6-b0ee-34109b7cf25e', "-",""))), 203, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-04'), 40, (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), null, 11.768923964695388, 2.4610877197653647, DATE('2020-06-01'), 39.92, 0.08, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('4d903bbe-4add-4eba-8cee-7de921429f77', "-",""))), 303, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-04'), 0, (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), (SELECT id FROM security WHERE original_id = 'DIMETEST01'), 35.47742081544845, 16.634469760745098, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('ee6f5135-a88b-4852-b3be-8e4503d434f8', "-",""))), 104, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-05'), 10, (SELECT id FROM security WHERE original_id = 'DIMETEST01'), null, 49.51287575660314, 13.877510643893597, DATE('2020-06-02'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('95453ba7-667f-4460-b36b-0e24f635a708', "-",""))), 204, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-05'), 10, (SELECT id FROM security WHERE original_id = 'DIMETEST01'), null, 37.38924874656132, 16.09438457563449, DATE('2020-06-02'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('28a3b470-231d-4533-aa2a-59590b480151', "-",""))), 304, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-05'), 0, (SELECT id FROM security WHERE original_id = 'DIMETEST01'), (SELECT id FROM security WHERE original_id = 'SPILTAN TEST'), 18.65048824002239, 5.00366735548301, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('675f50ee-48ff-4709-b53b-97169c5ddc83', "-",""))), 105, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-06'), 20, (SELECT id FROM security WHERE original_id = 'SPILTAN TEST'), null, 25.034593204195833, 22.167801316818913, DATE('2020-06-03'), 19.96, 0.04, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('98c68a9c-142c-47d0-8b21-4147c952501e', "-",""))), 205, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-06'), 20, (SELECT id FROM security WHERE original_id = 'SPILTAN TEST'), null, 12.602863875893721, 23.684735799634915, DATE('2020-06-03'), 19.96, 0.04, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('96d17db6-4d2d-4524-8287-3a8a4e159998', "-",""))), 305, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-06'), 0, (SELECT id FROM security WHERE original_id = 'SPILTAN TEST'), (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), 14.24559022245685, 39.14244160434181, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('f8e71dcb-a4d9-4cae-8f13-7622c9196caf', "-",""))), 106, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-07'), 30, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 4.100361943079733, 19.9778302310349, DATE('2020-06-04'), 29.94, 0.06, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('2fb9d714-0eed-4b66-8ba7-ebbf950b174e', "-",""))), 206, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-07'), 30, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), null, 35.46613918453494, 2.608602459459952, DATE('2020-06-04'), 29.94, 0.06, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('d18aebd4-53ef-4c6a-a4b1-26efa9710ced', "-",""))), 306, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-07'), 0, (SELECT id FROM security WHERE original_id = 'PASSIVETEST01'), (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), 3.9293210214428, 14.972200010132363, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('0b2e8826-e12c-454b-9782-0deb929bd7c0', "-",""))), 107, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-08'), 40, (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), null, 47.42911258654377, 38.88964935642677, DATE('2020-06-05'), 39.92, 0.08, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('4a85ed24-d266-4519-bee8-b90bfc4c2ff0', "-",""))), 207, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-08'), 40, (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), null, 36.25673978615836, 27.566903541025123, DATE('2020-06-05'), 39.92, 0.08, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('071eca58-0e81-4596-968f-48c40ec1e04d', "-",""))), 307, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-08'), 0, (SELECT id FROM security WHERE original_id = 'ACTIVETEST01'), (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), 42.80086121634427, 24.922556654005255, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('79d8be86-ec06-4cd6-b4b1-71370e35960c', "-",""))), 108, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-09'), 10, (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), null, 13.756375825970235, 30.216125474567768, DATE('2020-06-06'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('6f8a8eca-f7d7-4ac0-8245-40da6ef889a2', "-",""))), 208, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-09'), 10, (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), null, 31.439778118777962, 28.80271471113143, DATE('2020-06-06'), 10, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('dd0bfde1-db89-4562-958c-2d3a30426a95', "-",""))), 308, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-09'), 0, (SELECT id FROM security WHERE original_id = 'BALANCEDTEST01'), (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), 29.777381847555905, 48.98432460042636, null, 0, 0, 0);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('b17764f9-7564-4509-a974-ad18d0681de5', "-",""))), 109, (SELECT id FROM portfolio WHERE original_id = '123'), 11, DATE('2020-06-10'), 20, (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), null, 17.061228814712493, 38.78214608467783, DATE('2020-06-07'), 19.96, 0.04, 1);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('a1cb9726-341e-4bff-905a-129641afdfd8', "-",""))), 209, (SELECT id FROM portfolio WHERE original_id = '123'), 12, DATE('2020-06-10'), 20, (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), null, 3.256478938321339, 13.073155768828526, DATE('2020-06-07'), 19.96, 0.04, 1);
INSERT INTO portfolio_log (id, transaction_number, portfolio_id, transaction_code, transaction_date, c_total_value, security_id, c_security_id, amount, c_price, payment_date, c_value, provision, status)  VALUES  ((UNHEX(REPLACE('06aea64b-7275-48ac-a831-88e256dd14b9', "-",""))), 309, (SELECT id FROM portfolio WHERE original_id = '123'), 46, DATE('2020-06-10'), 0, (SELECT id FROM security WHERE original_id = 'FIXEDTEST01'), (SELECT id FROM security WHERE original_id = 'DIMETEST01'), 7.3276547663922775, 2.405765169057139, null, 0, 0, 1);