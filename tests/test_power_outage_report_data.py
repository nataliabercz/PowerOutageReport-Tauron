correct_configuration_one_address = {
    "sender_email": "sender@mail.com",
    "sender_email_password": "password",
    "addresses": [
        {
            "street_name": "StreetName",
            "house_number": "HouseNumber",
            "city": "City",
            "receivers_emails": [
                "receiver@mail.com"
            ]
        }
    ]
}

correct_configuration_multiple_addresses = {
    "sender_email": "sender@mail.com",
    "sender_email_password": "password",
    "addresses": [
        {
            "street_name": "StreetName1",
            "house_number": "HouseNumber1",
            "city": "City1",
            "receivers_emails": [
                "receiver@mail.com"
            ]
        },
        {
            "street_name": "StreetName2",
            "house_number": "HouseNumber2",
            "city": "City2",
            "receivers_emails": [
                "receiver1@mail.com", "receiver2@mail.com"
            ]
        }
    ]
}

test_response = '{"AddressPoint":null,"OutageItems":[{"OutageId":"id_1","StartDate":"s_date","EndDate":"e_date",' \
                '"Message":"msg","IsActive":true},{"OutageId":"id_2","StartDate":"s_date","EndDate":"e_date",' \
                '"Message":"msg","IsActive":false}]}'
test_response_adjusted = '{"AddressPoint":"","OutageItems":[{"OutageId":"id_1","StartDate":"s_date",' \
                         '"EndDate":"e_date","Message":"msg","IsActive":True},{"OutageId":"id_2",' \
                         '"StartDate":"s_date","EndDate":"e_date","Message":"msg","IsActive":False}]}'

email_template = 'From: {}\nTo: {}\nSubject: [TAURON] Planned power outage\n\nAREA: {}\nSTART: {}\nEND: {}\n' \
                 'DURATION: {} - {}'
