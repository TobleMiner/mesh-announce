import providers

class Source(providers.DataSource):
    def call(self):
        return float(open('/proc/uptime').read().split(' ')[0])

def get_source():
    return Source()
