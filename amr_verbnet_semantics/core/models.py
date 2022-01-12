"""
Models defined for the services
"""


class PredicateCalculus(object):
    def __init__(self, predicate, arguments, is_negative=False):
        self.predicate = predicate
        self.arguments = arguments
        self.is_negative = is_negative

    def __repr__(self):
        stmt = self.predicate + "(" + ", ".join(self.arguments) + ")"
        if self.is_negative:
            stmt = "NOT({})".format(stmt)
        return stmt

    def to_json(self):
        return {
            "predicate": self.predicate,
            "arguments": self.arguments,
            "is_negative": self.is_negative
        }


if __name__ == "__main__":
    pass

