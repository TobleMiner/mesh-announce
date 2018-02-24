import providers

class Source(providers.DataSource):
    def call(self):
        return True

def get_source():
    return Source()
