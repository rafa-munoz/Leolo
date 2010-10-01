"""
Code from "Getting Started with Pyparsing", by Paul McGuire.
"""
from pyparsing import *

and_ = CaselessLiteral("and")
or_ = CaselessLiteral("or")
not_ = CaselessLiteral("not")

searchTerm = Word(alphanums + "=" + "_") | quotedString.setParseAction(removeQuotes)
searchExpr = operatorPrecedence(searchTerm,
       [
       (not_, 1, opAssoc.RIGHT),
       (and_, 2, opAssoc.LEFT),
       (or_, 2, opAssoc.LEFT),
       ])

if __name__ == "__main__":
    tests = """\
        wood_is=white and blue or red
        wood and (blue or red)
        (steel or iron) and \"lime green\"
        not steel or iron and \"lime green\"
        not(steel or iron) and \"lime green\"""".splitlines()

    for t in tests:
        print t.strip()
        print searchExpr.parseString(t)[0]
        print

