import dreampylib
import config
import sys

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

if __name__ == '__main__':
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