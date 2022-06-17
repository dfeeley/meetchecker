class BaseChecker:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "Unnamed Checker")

    def run(self, data):
        filtered = self.check(data).copy()
        if len(filtered.index) == 0:
            return
        print(type(filtered))
        filtered["check_name"] = self.name
        filtered["reason"] = filtered.apply(self.get_reason, axis=1)
        return filtered
