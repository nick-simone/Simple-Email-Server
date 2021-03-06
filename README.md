# Simple-Email-Server
A simple email server built using python 3. 

## Dependancies
The server requires the packages flask, boto3, and sqlite3.

## Description
The server listens for POST requests on port 80 using two endpoints:
  - /send-email: listens for POST parameters from, to, subject, body_text, and body_html and sends an email using the service specified in the config.json file. A response from the service provider is returned on success and a response with status code 400 is returned if the email address is blacklisted.
  - /bounced-email: listens for POST parameter email_address, and adds the email provided to the sqlite3 database of blacklisted emails. A response with status code 200 is returned on success and a response with status code 400 is returned if the email is already present in the database.

## Use
Currently, there are two email "services" avaliable. The config file can be set for "AWS" or "Test". AWS functionality is implemented but I do not subscribe to the service so it will not work as-is. "Test" is useable, although it serves only as a test case for the successful sending of an email - it does nothing but return a response with status code 200. As an example, I've already blacklisted the address "nick@nick.com".

## Design
The server uses a factory class to generate subclasses of the EmailClient class specific to each email service depending on service specified in the config.json file. The sqlite3 database consists of one table with one field (email) and simply stores email addresses.
