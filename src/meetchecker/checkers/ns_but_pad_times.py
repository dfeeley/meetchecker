class Checker:
    def run(self, data):
        entry = data["entry"]
        return entry[(entry.fin_stat == "R") & (entry.num_pad_times > 0)]
