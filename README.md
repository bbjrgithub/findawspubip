## findawspubip.py:

Searches all regions in an AWS account for a specified public IP.

### Usage: 

**./findawspubip.py [public IP]**

### Example:

    $ ./findawspubip.py 52.9.137.45
    Searching for IP in: us-east-1
    Searching for IP in: us-east-2
    Searching for IP in: us-west-1

    IP 52.9.137.45 Found:

    ENI: eni-0c24eddb53e82f719, PrivateIP: 172.31.12.247, PublicIP: 52.9.137.45
