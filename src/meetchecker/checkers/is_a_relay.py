from .base import BaseChecker


class Checker(BaseChecker):
    def get_reason(self, row):
        return "Its a relay"

    def check(self, data):
        entry = data["entry"]
        filtered = entry.loc[(entry.ind_rel == "R")]
        return filtered
