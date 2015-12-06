import dreampylib
import config
import sys
import httplib
from datetime import datetime

version = '0.0.1'

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
		conn = httplib.HTTPConnection(config.ip_check_hostname)
		conn.request("GET", config.ip_check_path)
		resp = conn.getresponse()
		if resp.status != 200:
			raise Exception('Could not retrieve IP address. Server returned ' + str(resp.status))
		data = resp.read()
		return data
	except:
		raise Exception('Failed to retrieve IP address.')

def check_service_up(ip_str):
	headers = {"Host": config.dns_check_host}
	conn = httplib.HTTPConnection(ip_str)
	conn.request("GET", config.dns_check_path, "", headers)
	resp = conn.getresponse()
	if resp.status != 200:
		raise Exception('DNS Check failed. Status: ' + str(resp.status))
	data = resp.read()
	if data.strip() != config.dns_check_response:
		raise Exception('Wrong data returned from DNS Check: ' + data.strip())

def check_commands(connection):
	if not check_commands_avail(connection, ["dns-add_record", "dns-list_records", "dns-remove_record"]):
		raise Exception('No access to appropriate dns commands.')

def get_dns_records(connection):
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

def update_record(connection, rec, name, zone, ip_addr):
	if rec:
		res = connection.dns.remove_record(record = rec['record'], type=rec['type'], value=rec['value'])
		print(res)
	new_record = name + '.' + zone
	new_type = 'A'
	value = ip_addr.strip()
	comment = ''
	if rec:
		comment = comment + 'Updated '
	else:
		comment = comment + 'Added '
	comment = comment + 'by PS AutoDNS ' + version + ' at '
	comment = comment + datetime.now().isoformat()
	res = connection.dns.add_record(record=new_record, type=new_type, value=value, comment=comment)
	print(res)

if __name__ == '__main__':
	try:
		ip_addr = get_ip_address()
		check_service_up(ip_addr)
		connection = get_connection()
		recs = get_dns_records(connection)
		for sub in config.subdomains:
			sub_rec = get_a_rec_for_zone(recs, sub['name'], sub['zone'])
			if should_update_record(sub_rec, ip_addr):
				update_record(connection, sub_rec, sub['name'], sub['zone'], ip_addr)
	except Exception as e:
		if e.args and len(e.args) > 0:
			print_err(e.args[0])