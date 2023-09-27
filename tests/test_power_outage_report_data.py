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
test_response_replaced = '{"AddressPoint":"","OutageItems":[{"OutageId":"id_1","StartDate":"s_date",' \
                         '"EndDate":"e_date","Message":"msg","IsActive":True},{"OutageId":"id_2","StartDate":"s_date",' \
                         '"EndDate":"e_date","Message":"msg","IsActive":False}]}'
test_response_adjusted = {'AddressPoint': '', 'OutageItems': [{'EndDate': 'e_date', 'IsActive': True, 'Message': 'msg',
                                                               'OutageId': 'id_1', 'StartDate': 's_date'},
                                                              {'EndDate': 'e_date', 'IsActive': False, 'Message': 'msg',
                                                               'OutageId': 'id_2', 'StartDate': 's_date'}]}

outage_items = [{'OutageId': 'id_1',
                 'StartDate': 's_date_1',
                 'EndDate': 'e_date_1',
                 'Message': 'StreetName'},
                {'OutageId': 'id_2',
                 'StartDate': 's_date_2',
                 'EndDate': 'e_date_2',
                 'Message': 'OtherStreet'}]

email_template = 'From: {}\nTo: {}\nSubject: [TAURON] Planned power outage - {}\n\nAREA: {}\nSTART: {}\nEND: {}\n' \
                 'DURATION: {} - {}'

sent_emails_folder = '[Gmail]/Sent Mail'
sent_email_message_bytes = b'Return-Path: <sender@mail.com>\r\n' \
                           b'Received: from LAPTOP-XYZ.lan ([0.0.0.0])\r\n' \
                           b'by smtp.gmail.com with ESMTPSA id l25-20020a2m3024657ljg.111.2023.09.27.06.43.59\r\n' \
                           b'for <receiver@mail.com>\r\n' \
                           b'(version=TLS1_3 cipher=TLS_AES_256_GCM_SHA384 bits=256/256);\r\n' \
                           b'Wed, 27 Sep 2023 02:43:59 -0700 (PDT)\r\n' \
                           b'Message-ID:<6513f95f.2e0a0220.53138.8d3c@mx.google.com>\r\n' \
                           b'Date: Wed, 27 Sep 2023 06:43:59 -0700 (PDT)\r\n' \
                           b'From: sender@mail.com\r\n' \
                           b'To: receiver@mail.com\r\n' \
                           b'Subject: [TAURON] Planned power outage - StreetName\r\n\r\n' \
                           b'AREA: ... StreetName ...\r\n' \
                           b'START: 27/09/2023\r\n' \
                           b'END: 27/09/2023\r\n' \
                           b'DURATION: 07:00:00 - 16:00:00\r\n'
