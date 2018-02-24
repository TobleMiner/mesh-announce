import providers
import multiprocessing

class Source(providers.DataSource):
    def call(self):
        return multiprocessing.cpu_count()

def get_source():
    return Source()
