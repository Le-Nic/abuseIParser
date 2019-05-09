# abuseIParser
Python script for parsing batch of IPs and aggregating the results from AbuseIPDB API.  

1. Select txt file containing list of IPs
2. Select json/csv format to save the output in
3. ???
4. Profit

## Prerequisites
- Python 3
- AbuseIP DB API Key _(replace the API_KEY on line 12 of the script)_

## Usage Example
#### JSON output
``` BASH
python abuseIParser.py -i samples/IPs.txt -o samples/output.json -d 15 -v -t 2
```

#### CSV output
``` BASH
python abuseIParser.py -i samples/IPs.txt -o samples/output.csv -d 15 -v -t 2
```

#### Arguments
``` BASH
  -h, --help                        show this help message and exit
  -i INPUT, --input INPUT           File containing IPv4 or IPv6 Addresses
  -o OUTPUT, --output OUTPUT        Output's file name and type. Default: ./lazyname.json
  -d DAYS, --days DAYS              Check for IP Reports in the last n days. Default: 30
  -v, --verbose                     If set, reports will include the country name field. Default: None
  -t TIMEOUT, --timeout TIMEOUT     Sleep for n seconds before each request. Default: 0
  -f, --formatted                   If set, reports will be formatted for csv output. Default: None
```
