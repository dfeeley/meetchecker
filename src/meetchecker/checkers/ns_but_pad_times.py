class Checker:
    def run(self, data):
        entries = data["entries"]
        return entries[(entries.fin_stat == "R") & (entries.num_pad_times > 0)]
