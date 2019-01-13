import providers
from providers.util import call
import re

re_mac = re.compile('([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}')

class Source(providers.DataSource):
    def required_args(self):
        return ['batadv_dev']

    def call(self, batadv_dev):
        lines = call(['batctl', '-m', batadv_dev, 'o'])
        mesh_mac = re_mac.search(lines[0]).group(0)
        neighbours = {}
        for line in lines[2:]:
            fields = line.replace('(', '').replace(')', '').split()
            if fields[0] == fields[3]:
                neighbours[fields[0]] = {'lastseen': float(fields[1].strip('s')), 'tq': int(fields[2])}
        return {mesh_mac: neighbours}
