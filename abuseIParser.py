import argparse
import csv
import json
import sys
import os
from pathlib import Path
from time import sleep
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_KEY = 'YOUR_API_KEY'

def doStuff(settin):
    req_url = 'https://www.abuseipdb.com/api/v2/check/?'
    req_fields = {
        'key': API_KEY,
        'maxAgeInDays': settin['d']
    }

    if settin['v']:
        req_fields['verbose'] = True

    with open(settin['i'], 'r') as f_in:
        print('>> [IO] Input Path:', settin['i'])
        print('>> [IO] Output path:', settin['o'])
        print('>> [CONFIG] url:', req_url)
        print('>> [CONFIG] maxAgeInDays:', settin['d'])
        print('>> [CONFIG] verbose:', settin['v'])
        print('>> [CONFIG] timeout:', settin['t'])
        print('>> [CONFIG] formatted:', settin['f'])

        ips = f_in.readlines()
        lines = len(ips)

        for i, dirty_ip in enumerate(ips, 1):
            ip = dirty_ip.strip()
            if ip:
                print('>> [PROCESSING] {0}/{1} IP: {2}'.format(i, lines, ip), end='\r')

                try:
                    sleep(settin['t'])
                except TypeError as e:
                    print('\n>> [ERROR] Invalid timeout value')
                    exit(2)

                req_fields['ipAddress'] = ip

                try:
                    req = Request(req_url + urlencode(req_fields))
                    req_read = urlopen(req).read()
                    res = json.loads(req_read.decode())

                except Exception as e:
                    print('\n>> [ERROR]', e)
                    print('\t> [INFO] Make sure you have a valid API key / limits')
                    exit(1)

                if not res:
                    continue

                if settin['ext'] == '.json':
                    with open(settin['o'], 'r') as f_out:
                        try:
                            data = json.load(f_out)
                        except ValueError:
                            data = []

                        if isinstance(data, (list,)):
                            data.append(res)
                        else:
                            data = [data, res]

                    with open(settin['o'], 'w+') as f_out:
                        json.dump(data, f_out)

                elif settin['ext'] == '.csv':
                    with open(settin['o'], 'a+') as f_out:
                        data = res['data']
                        data_keys = data.keys()

                        data_writer = csv.DictWriter(f_out, fieldnames=data_keys, delimiter=',', lineterminator='\n')

                        if settin['f']:
                            reports = data.pop('reports', [])
                            data_writer.writeheader()
                            data_writer.writerows([data])

                            if reports:
                                reports_keys = reports[0].keys()
                                reports_writer = csv.DictWriter(f_out, fieldnames=reports_keys, delimiter=',', lineterminator='\n')
                                reports_writer.writeheader()
                                reports_writer.writerows(reports)

                            f_out.write('\n')

                        else:
                            if settin['o_isnew']:
                                data_writer.writeheader()
                                settin['o_isnew'] = False
                            data_writer.writerows([data])

def main(parser):
    args = parser.parse_args()

    if args.input:
        settin = {}

        ''' INPUT FILE '''
        p = Path(args.input).resolve()
        if p.is_file():
            settin['i'] = p
        else:
            print('>> [ERROR] Invalid input')
            exit(1)

        ''' OUTPUT TYPE '''
        ext = ['.json', '.csv']
        if args.output:
            settin['ext'] = os.path.splitext(args.output)[1]
        else:
            settin['ext'] = None
            args.output = 'lazyname'  # default output filename

        if settin['ext'] not in ext:
            settin['ext'] = ext[0]
            print('>> [WARNING] Unsupported format is specified, output format changed to', settin['ext'][1:])

        ''' OUTPUT FILE '''
        p = Path(args.output)

        if p.is_file():  # specified path
            settin['o'] = Path(str(p.parents[0]) + '/' + p.stem + settin['ext']).resolve()
            print('>> [WARNING] Results will be appended to existing file')

        elif p.is_dir():  # unspecified file name
            settin['o'] = Path(str(p) + '/' + p.stem + settin['ext']).resolve()

        elif not p.parents[0].name:  # unspecified path
            settin['o'] = Path( os.path.dirname(os.path.realpath(__file__)) + '/' + p.stem + settin['ext'] )

        else:  # specified directory
            Path(p.parents[0]).mkdir(parents=True, exist_ok=True)
            settin['o'] = Path(str(p.parents[0]) + '/' + p.stem + settin['ext']).resolve()

        try:
            settin['o'].touch(exist_ok=False)
            settin['o_isnew'] = True
        except FileExistsError:
            settin['o_isnew'] = False

        ''' DAYS '''
        if args.days:
            settin['d'] = str(args.days)
        else:
            settin['d'] = '30'
            print('>> [WARNING] maxAgeInDays defaulted to 30')

        ''' VERBOSE '''
        settin['v'] = args.verbose

        ''' FORMATTED '''
        settin['f'] = args.formatted

        ''' TIMEOUT '''
        settin['t'] = int(args.timeout) if args.timeout else 0

        settin['i'] = str(settin['i'])
        settin['o'] = str(settin['o'])

        doStuff(settin)
        exit(0)

    else:
        parser.print_help()


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('[ERROR] %s\n' % message)
        sys.stderr.write('\tinput -h or --help for proper usage and arguments help.\n')
        sys.exit(2)

if __name__ == '__main__':

	parser = MyParser(
			prog = 'abuseIParser',
			usage = '%(prog)s [options]',
			formatter_class = argparse.RawTextHelpFormatter,
			description = """
			a simple abuseIPDB Parser""")

	parser.add_argument(
		'-i', '--input',
		dest = 'input',
		metavar = 'INPUT',
		help = 'File containing IPv4 or IPv6 Addresses')

	parser.add_argument(
		'-o', '--output',
		dest = 'output',
		metavar = 'OUTPUT',
		help = 'Output\'s file name and type. Default: ./lazyname.json')

	parser.add_argument(
		'-d', '--days',
		dest = 'days',
		metavar = 'DAYS',
		help = 'Check for IP Reports in the last n days. Default: 30')

	parser.add_argument(
		'-v', '--verbose',
		dest = 'verbose',
		action = 'store_true',
		help = 'If set, reports will include the country name field. Default: None')

	parser.add_argument(
		'-t', '--timeout',
		dest = 'timeout',
		metavar = 'TIMEOUT',
		help = 'Sleep for n seconds before each request. Default: 0')

	parser.add_argument(
		'-f', '--formatted',
		dest = 'formatted',
		action = 'store_true',
		help = 'If set, reports will be formatted for csv output. Default: None')

	try:
		main(parser)
	except KeyboardInterrupt:
		print('\n>> [EXIT] Keyboard Interrupted')

		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
