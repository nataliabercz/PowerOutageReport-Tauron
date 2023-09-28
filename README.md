# PowerOutageReport - Tauron

## Description

PowerOutageReport allows you to configure Tauron power outage reports for selected addresses.

You can sign up for notifications on Tauron's official website, but then almost every day you will receive 
e-mails about power failures on a lot of streets in your area - not only on the specific 
streets that concerns you.

PowerOutageReport checks recently sent e-mails (their number can be configured) and therefore 
only sends one failure report.

## Instructions

### 1. Installing all needed packages.
Install Python and all packages from `requirements.txt` file.

### 2. Filling in configuration file

Fill in the configuration file: `configuration.json`. You can find it in the `data` directory.

#### 1.1 Fields description

- sender_email - e-mail address, e-mails will be sent from this address
- sender_email_password - e-mail password for e-mail address (check subchapter Getting sender_email_password)
- addresses - list of addresses
- street_name - name of street
- house_number - number of house / building
- city - name of city where the street is
- receivers_emails - list of e-mail addresses when the power outage reports will be sent

#### 1.2 Example configuration file

```
{
  "sender_email": "sender@gmail.com",
  "sender_email_password": "password123",
  "addresses": [
    {
      "street_name": "Street1",
      "house_number": "10",
      "city": "City1",
      "receivers_emails": ["receiver@example.com"]
    },
    {
      "street_name": "Street2",
      "house_number": "20",
      "city": "City2",
      "receivers_emails": ["receiver1@example.com", "receiver2@example.com"]
    }
  ]
}
```

#### 1.3 Getting sender_email_password

*Note: The domain name for sender e-mail address should be gmail.com.*

1. Go to the Google account - `Security` tab: https://myaccount.google.com/security.
    <img src="./images/security_tab.png" width="400"/>

2. Go to `How you sign in to Google` field and choose `2-Step Verification`.

    *If 2-Step Verification is not turned on you need to set it first.*
    
    <img src="./images/two_steps_verification.png" width="400"/>

3. Scroll down and go to the `App passwords` section.
    
    <img src="./images/app_passwords.png" width="400"/>

4. Fill in the `App name` and click `Create` button.
    
    <img src="./images/create_password.png" width="400"/>

5. Copy generated password.
    
    <img src="./images/generated_password.png" width="400"/>

6. Paste generated password to `configuration.json` file and remove all spaces.
   
    *It should look like: `oaksrbampblkvusr`.*

### 3. Adding script to Startup Apps 

To ensure that the script runs frequently enough, it should be executed automatically.
You can add it to the `Startup Apps`, so it will be launched every time you turn on your computer.

1. Right-click on `power_outage_report.py` and choose `Create shortcut`.

   <img src="./images/create_shortcut.png" width="600"/>

2. Open the `Startup` directory.

   1.1 Click `Windows Key + R`. 

   1.2 In the Run window, in the Open field type `shell:startup`.

   1.3 Click `OK`.

    <img src="./images/shell_startup.png" width="300"/>

3. Put `power_outage_report.py - Shortcut` in the `Startup` directory.

    <img src="./images/startup_directory.png" width="600"/>

### 4. Additional settings

1. If you send many e-mails from your gmail mailbox, you can change the number of sent emails that will be checked.
   Currently, it is set to 20. This means if any of the last 20 emails was a power outage report, 
   a new message will not be generated.

   1.1 Open `email_sender.py`. 

   1.2 Change `sent_messages_number` variable to the desired number (`type: int`).
