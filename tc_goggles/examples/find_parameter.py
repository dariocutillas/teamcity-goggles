import os
import re
import itertools
import argparse

from tc_goggles.parameter_filters import name_matches, value_matches, inherited
from tc_goggles.endpoint import ServerConfig, TeamCityEndPoint, Auth


def find_params(parameter_filter):
    server_config = ServerConfig(
        # https server address
        uri = os.environ["TEAMCITY_SERVER"],
        # Use Auth.token(token) or Auth.basic(username, password)
        auth = Auth.token(os.environ["TEAMCITY_ACCESS_TOKEN"]))
        
    tc = TeamCityEndPoint.create(server_config)
    
    # Look-up in both build configurations and templates
    build_types = itertools.chain(tc.build_configurations(), tc.build_templates())

    # Get the parameter and build_type constrained to the filter
    params = ((parameter, build_type) \
                for build_type in build_types \
                for parameter in build_type.parameters() if parameter_filter(parameter))

    for (param, build_type) in params:
        msg = f'{build_type.web_url}  {param.name}  {param.value}'
        print(msg)
        

def main():
    parser = argparse.ArgumentParser(description='Find build types containing parameters with specific values.')
    parser.add_argument('name', type=str, help='The name of the parameter.')
    parser.add_argument('--values', type=str, metavar='VALUE', nargs='+', help='Optional list of values the parameter should have.')

    args = parser.parse_args()

    # Build the parameter filter based on the arguments

    # A convenient list of parameter filters is available on the parameter_filter module.
    # Operators |, & and ~ are overloaded. Alteratively it is possible to define a custom function.
    parameter_filter = ~inherited \
                      & name_matches(args.name)

    if args.values:
        regex = f"({'|'.join(args.values)})" 
        parameter_filter = parameter_filter & value_matches(regex)
     
    find_params(parameter_filter)
    
if __name__ == '__main__':
    main()
