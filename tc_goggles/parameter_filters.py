"""
Predefined filters on parameters.
"""

import re


class ParameterFilter:

    def __init__(self, func):
        self._func = func

    def __call__(self, parameter):
        return self._func(parameter)

    def __or__(self, other):
        return ParameterFilter(lambda p : self(p) or other(p))

    def __and__(self, other):
        return ParameterFilter(lambda p: self(p) and other(p))
    
    def __invert__(self):
        return ParameterFilter(lambda p: not self(p))


def name_matches(regex, *options):
   return ParameterFilter(lambda p : not p.name is None and re.search(regex, p.name, *options))


def value_matches(regex, *options):
    return ParameterFilter(lambda p : not p.value is None and re.search(regex, p.value, *options))


inherited = ParameterFilter(lambda p : p.inherited == True)


