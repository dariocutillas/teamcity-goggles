# TeamCity Goggles

A utility module to perform some queries on TeamCity REST API. Currently
the set of supported REST operations if very limited to the needs I've
had.

Install with:

```
pip install https://github.com/dariocutillas/teamcity-goggles
```

Or clone & install with:

```
pip install -e .
```

Have a look at the `examples` package modules for usage examples. To run any of the
tools in the `examples` package use:

```
python -m tc_googles.examples.<module_name> <arguments>
```

For example:

```
python -m tc_goggles.examples.find_parameter MY_PARAMETER --values A B C
```

Requires Python > 3.6. 
