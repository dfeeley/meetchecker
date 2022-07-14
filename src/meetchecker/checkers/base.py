class BaseChecker:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "Unnamed Checker")
        self.color = kwargs.get("color")

    def run(self, data):
        filtered = self.check(data).copy()
        if len(filtered.index) == 0:
            return
        filtered["check_name"] = self.name
        filtered["reason"] = filtered.apply(self.get_reason, axis=1)
        return filtered
