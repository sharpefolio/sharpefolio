# Commands for generating a self signed certificate

Replace `example.sharpefolio.com` with the domain (or IP) you are creating the
certificate for. If this is for the AWS account, you can probably use any
domain.

1. `openssl genrsa -des3 -out example.sharpefolio.com.server.key 2048`
    1. **pass phrase:** `sharpefolio`
1. `openssl req -new -key example.sharpefolio.com.server.key -out example.sharpefolio.com.server.csr`
    1. **Country:** `US`
    1. **State:** `California`
    1. **Locality:**
    1. **Organization:** `sharpefolio`
    1. **Organizational Unit Name:**
    1. **Common Name:** `example.sharpefolio.com`
    1. **Email:** `example@sharpefolio.com`
    1. **Challenge:**
    1. **Company Name:**
1. `openssl rsa -in example.sharpefolio.com.server.key -out example.sharpefolio.com.server.key`
1. `openssl x509 -req -days 730 -in example.sharpefolio.com.server.csr -signkey example.sharpefolio.com.server.key -out example.sharpefolio.com.server.crt`
