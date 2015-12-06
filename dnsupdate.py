import dreampylib
import config
import sys
import httplib

def print_err(msg):
	sys.stderr.write(msg)

def check_command_avail(conn, name):
	return name in [x[0] for x in conn.AvailableCommands()]

def check_commands_avail(conn, names):
	for name in names:
		if not check_command_avail(conn, name):
			return False
	return True

def get_subdomain(record):
	sub = record['record'].replace(record['zone'], '')
	if len(sub) > 0 and sub[-1] == '.':
		sub = sub[:-1]
	return sub

def get_a_recs(records, name):
	name = name.lower()
	recs = []
	for rec in records:
		rec_name = get_subdomain(rec)
		if rec_name.lower() == name:
			recs.append(rec)
	return recs

def get_a_rec_for_zone(records, name, zone):
	recs = get_a_recs(records, name)
	zone = zone.lower()
	res = [x for x in recs if x['zone'].lower() == zone]
	return res[0] if len(res) > 0 else None

def get_ip_address():
	try:
		conn = httplib.HTTPConnection("paulsanford.net")
		conn.request("GET", "/ip.php")
		resp = conn.getresponse()
		if resp.status != 200:
			return None
		data = resp.read()
		return data
	except:
		return None

def check_service_up(ip_str):
	try:
		headers = {"Host": "DNS_CHECK.paulsanford.int"}
		conn = httplib.HTTPConnection(ip_str)
		conn.request("GET", "/DNS_CHECK", "", headers)
		resp = conn.getresponse()
		if resp.status != 200:
			return False
		data = resp.read()
		if data.strip() != "PS NETWORK OK":
			return False
	except:
		print("Exception")
		return False
	return True

def check_commands(connection):
	if not check_commands_avail(connection, ["dns-add_record", "dns-list_records", "dns-remove_record"]):
		raise Exception('No access to appropriate dns commands.')

def get_dns_records():
	connection = get_connection()
	check_commands(connection)
	return connection.dns.list_records()

def get_connection():
	connection = dreampylib.DreampyLib(config.user, config.key)
	if not connection.IsConnected():
		raise Exception('Unable to connect to Dreamhost API')
	return connection

def filter_dns_records_by_zone(records, zone):
	return [x for x in recs if x['zone'].lower() == zone.lower()]

def should_update_record(record, ip_addr):
	return record == None or record['value'].strip() != ip_addr.strip()


if __name__ == '__main__':
	try:
		ip_addr = get_ip_address()
		recs = get_dns_records()
		for sub in config.subdomains:
			sub_rec = get_a_rec_for_zone(recs, sub['name'], sub['zone'])
			if should_update_record(sub_rec, ip_addr):
				print('Updating ' + sub['name'] + ' for zone ' + sub['zone'])
	except Exception as e:
		if e.args and len(e.args) > 0:
			print_err(e.args[0])

if __name__ == '__main__b':
	ip_addr = get_ip_address()
	print("IP Address: " + ip_addr)
	print("Is host up: " + "yes" if check_service_up(ip_addr) else "no")

if __name__ == '__main__a':
	connection = dreampylib.DreampyLib(config.user, config.key)
	if connection.IsConnected():
		if not check_commands_avail(connection, ["dns-add_record", "dns-list_records", "dns-remove_record"]):
			print_err("No access to appropriate dns commands.")

		recs = connection.dns.list_records()

		if len(sys.argv) <= 2:
			filtered_recs = [x for x in recs if x['zone'] == 'paulsanford.net']

			print('Found ' + str(len(filtered_recs)) + ' records')
		else:
			rec = get_a_rec_for_zone(recs, sys.argv[1], sys.argv[2])
			if rec:
				print(rec)
			else:
				print('Record not found')