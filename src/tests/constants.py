from .auth.auth import BearerAuth

fund_ids = {
    "passivetest01": "03568d76-93f1-3a2d-9ed5-b95516546548",
    "activetest01": "dc856547-449b-306e-80c9-05ef8a002a3a",
    "balancedtst01": "3073d4fe-78cc-36ec-a7e0-9c24944030b0",
    "fixedtest0": "8cd9b437-e524-3926-a3f9-969923cf51bd",
    "dimetest01": "79f8da68-6bdc-3a24-acde-327aa14e2546",
    "spiltan_test": "098a999d-65ae-3746-900b-b0b33a5d7d9c"
}

security_ids = {
    "PASSIVETEST01": "9bed2c6f-8f2c-4e6d-a711-d75cb2474616",
    "ACTIVETEST01": "d84dfb1a-3230-4d0e-abcb-2a9f9b118afa",
    "BALANCEDTEST01": "87c526df-c4b0-42d2-8202-07c990c725db",
    "FIXEDTEST01": "a2c14970-161b-407a-9961-d1b14739ec2a",
    "DIMETEST01": "49d73d12-3061-469a-ba67-0b4a906dd4fc",
    "SPILTAN TEST": "b01f0d42-e133-44f1-a3c2-d0b560b868ae"
}

invalid_uuids = ["potato", "`?%!", "äö", "Правда"]

access_token_from_wrong_keycloak = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3eFQ5OU1BWGhOS1RYSnlvXzVibDF3N3BOTmRpakgxUjZBakhwZGhoelZvIn0.eyJleHAiOjE2Mzk3NTExNzcsImlhdCI6MTYzOTc1MDg3NywiYXV0aF90aW1lIjoxNjM5NzUwODc2LCJqdGkiOiI3NzUyODg5Zi05ZWFjLTQ1MzUtOTk1NC0wMGQ2NzEyN2IxYjAiLCJpc3MiOiJodHRwczovL3N0YWdpbmctc2VsaWdzb24tYXV0aC5tZXRhdGF2dS5pby9hdXRoL3JlYWxtcy9zZWxpZ3NvbiIsImF1ZCI6WyJhcGkiLCJhY2NvdW50Il0sInN1YiI6IjM1MjVkNTgxLTA1YjYtNGE2MS04OGI1LWJkOTllYWVlZDUxOCIsInR5cCI6IkJlYXJlciIsImF6cCI6ImFwcCIsInNlc3Npb25fc3RhdGUiOiJhMDJjNjZiNC1mMmQ3LTQxOTgtOWE1Zi1lNDZlZTU1Zjg1NjIiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtc2VsaWdzb24iLCJvZmZsaW5lX2FjY2VzcyIsImFub255bW91cyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6ImEwMmM2NmI0LWYyZDctNDE5OC05YTVmLWU0NmVlNTVmODU2MiIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IkFub255bW91cyBVc2VyIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYW5vbnltb3VzIiwiZ2l2ZW5fbmFtZSI6IkFub255bW91cyIsImZhbWlseV9uYW1lIjoiVXNlciIsImVtYWlsIjoiYW5vbnltb3VzQGV4YW1wbGUuY29tIn0.PUIoBGkxAXXtLz8IAwD83erxeGTgTlVxSmfK1d02fe-2jjIc8Q2l9dj4rxFOtgEck38F6iR49gOIy3y-N0dT7vxD5R1C4GPwafZR_L5R9MtWhZuL20bsgyWG5uLCJsCjgJ-QyHHfRzRWuFPnCH_ai6tQOsbBuDfSPOOBEKfZt2MaBL-kJGhVIdVWLTGxN6r1saV5QIGXwq6N-amJYMrvLiOUk-gjj658qGs7ZUwP8SbX2z24f_PolGrkpdqf-O4yizIrMVpydZC80EifJ4hMo-In29asy5ATCQD1wd0dk94kW12CoFdYIjjGJuYiOervW7PaHAFqUvozsACtQ1i6ew" # noqa
access_token_invalid = "eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.o1hC1xYbJolSyh0-bOY230w22zEQSk5TiBfc-OCvtpI2JtYlW-23-8B48NpATozzMHn0j3rE0xVUldxShzy0xeJ7vYAccVXu2Gs9rnTVqouc-UZu_wJHkZiKBL67j8_61L6SXswzPAQu4kVDwAefGf5hyYBUM-80vYZwWPEpLI8K4yCBsF6I9N1yQaZAJmkMp_Iw371Menae4Mp4JusvBJS-s6LrmG2QbiZaFaxVJiW8KlUkWyUCns8-qFl5OMeYlgGFsyvvSHvXCzQrsEXqyCdS4tQJd73ayYA4SPtCb9clz76N1zE5WsV4Z0BYrxeb77oA7jJhh994RAPzCG0hmQ" # noqa
gibberish_token = "aGVhZGVy.cGF5bG9hZA==.c2lnbmF0dXJl"
unicode_token = "äöПравда?%!.potato"

invalid_access_tokens = [access_token_from_wrong_keycloak, access_token_invalid, gibberish_token, unicode_token, ""]

invalid_auths = list(map(lambda x: BearerAuth(token=x), invalid_access_tokens))