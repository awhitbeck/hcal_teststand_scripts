# Notes: keep this script compatible with Python 2.4.

from re import search

def parse_ts_configuration(f):		# This function is a clone of the function of the same name in hcal_teststand but modified to be compatible with Python 2.4.
	variables = ["name", "fe_crates", "ngccm_port", "uhtr_ip_base", "uhtr_slots", "glib_slot", "mch_ip", "amc13_ips", "qie_slots"]
	teststand_info = {}
	raw = ""
	if ("/" in f):
		raw = open("{0}".format(f)).read()
	else:
		raw = open("configuration/" + f).read()
	teststands_raw = raw.split("%%")
	for teststand_raw in teststands_raw:
		lines = teststand_raw.strip().split("\n")
		ts_name = ""
		for variable in variables:
			for line in lines:
				if variable in line:
					if (variable == "name"):
						ts_name = search(variable + "\s*=\s*(.+)", line).group(1)
						teststand_info[ts_name] = {}
					elif (variable == "fe_crates"):
						value = search(variable + "\s*=\s*(.+)", line).group(1)
						teststand_info[ts_name][variable] = [int(i) for i in value.split(",")]
					elif (variable == "ngccm_port"):
						value = search(variable + "\s*=\s*(.+)", line).group(1)
						teststand_info[ts_name][variable] = int(value)
					elif (variable == "uhtr_ip_base"):
						value = search(variable + "\s*=\s*(.+)", line).group(1)
						teststand_info[ts_name][variable] = value.strip()
					elif (variable == "uhtr_slots"):
						value = search(variable + "\s*=\s*(.+)", line).group(1)
						teststand_info[ts_name][variable] = [int(i) for i in value.split(",")]
					elif (variable == "glib_slot"):
						value = search(variable + "\s*=\s*(.+)", line).group(1)
						teststand_info[ts_name][variable] = int(value)
					elif (variable == "mch_ip"):
						value = search(variable + "\s*=\s*(.+)", line).group(1)
						teststand_info[ts_name][variable] = value.strip()
					elif (variable == "amc13_ips"):
						value = search(variable + "\s*=\s*(.+)", line).group(1)
						teststand_info[ts_name][variable] = [i.strip() for i in value.split(",")]
					elif (variable == "qie_slots"):
						value = search(variable + "\s*=\s*(.+)", line).group(1)
						crate_lists = value.split(";")
						teststand_info[ts_name][variable] = []
						for crate_list in crate_lists:
							if crate_list:
								teststand_info[ts_name][variable].append([int(i) for i in crate_list.split(",")])
							else:
								teststand_info[ts_name][variable].append([])
	return teststand_info

def make_amc13_configs(f):
	names = []
	ts_info = parse_ts_configuration(f)
	for name, info in ts_info.iteritems():
		if info:
			string = ""
			if name == "904":		# A temporary kludge until I figure this out better.
				string = '''
<?xml version="1.0" encoding="UTF-8"?>
<connections>
	<connection id="T1" uri="chtcp-2.0://localhost:10203?target=''' + info["amc13_ips"][0] + ''':50001" address_table="file:///opt/cactus/etc/amc13/AMC13XG_T1.xml" />
	<connection id="T2" uri="chtcp-2.0://localhost:10203?target=''' + info["amc13_ips"][1] + ''':50001" address_table="file:///opt/cactus/etc/amc13/AMC13XG_T2.xml" />
</connections>'''.strip()
			else:
				string = '''
<?xml version="1.0" encoding="UTF-8"?>
<connections>
	<connection id="T1" uri="chtcp-2.0://localhost:10203?target=''' + info["amc13_ips"][0] + ''':50001" address_table="file:///opt/cactus/etc/amc13/AMC13XG_T1_v0x4002.xml" />
	<connection id="T2" uri="chtcp-2.0://localhost:10203?target=''' + info["amc13_ips"][1] + ''':50001" address_table="file:///opt/cactus/etc/amc13/AMC13XG_T2_v0x21.xml" />
</connections>'''.strip()
			try:
				out = open("configuration/amc13_" + name + "_config.xml", "w")
				out.write(string)
				names.append(name)
			except Exception, ex:		# This notation is compatible with older versions of Python. It's good to keep this compatible so that the script can be run from the B904 head node.
				print ex
		else:
			print "ERROR: Didn't make an AMC13 configuration file for " + name + "."
	return names

def make_setup_scripts(f):
	names = []
	ts_info = parse_ts_configuration(f)
	for name, info in ts_info.iteritems():
		string = ""
		if info:
			if name == "bhm":
				string = '''
source /nfshome0/hcalsw/bin/env.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ngccm/lib
export PATH=$PATH:/opt/ngccm/bin
				'''.strip()
			elif name == "904":
				string = '''
source /nfshome0/hcalsw/bin/env.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/nfshome0/hcalpro/ngFEC
export PATH=$PATH:/nfshome0/hcalpro/ngFEC
				'''.strip()
			elif name == "fnal":
				string = '''
source /home/hcalpro/tote/env.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/hcalpro/ngFEC
export PATH=$PATH:/home/hcalpro/ngFEC
				'''.strip()
			try:
				out = open("configuration/setup_" + name + ".sh", "w")
				out.write(string)
				names.append(name)
			except Exception, ex:
				print ex
		else:
			print "ERROR: Didn't make an setup script for " + name + "."
	return names

if __name__ == "__main__":
	make_amc13_configs("teststands.txt")
	make_setup_scripts("teststands.txt")

