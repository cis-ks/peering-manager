import json
import re
import subprocess

from django.conf import settings


def call_irr_resolver(cmd, object, address_family=6):
    """
    Call a subprocess to expand the given Object with the given cmd.

    Supported cmd's:
    'as_set_prefixes' - resolve all Prefixes for an AS-SET
    'as_set_to_asn'   - resolve all ASNs within an AS-SET
    """
    resolvedobject = []

    if not object:
        return resolvedobject

    # Prepare bgpq3-command with arguments to get a JSON result
    command = [
        settings.BGPQ3_PATH,
        "-h",
        settings.BGPQ3_HOST,
        "-S",
        settings.BGPQ3_SOURCES,
    ]

    # Add options depending on given cmd
    if cmd == 'as_set_prefixes' :
        command.extend([ "-{}".format(address_family), "-A", ])
    elif cmd == 'as_set_to_asn' :
        command.extend([ "-f", "1", ])
    else:
        return resolvedobject

    command.extend([ "-j", "-l", "object_list", object, ])

    if cmd in [ 'as_set_prefixes' ]:
        # Merge user settings to command line right before the name of the prefix list
        if settings.BGPQ3_ARGS:
            index = len(command) - 3
            command[index:index] = settings.BGPQ3_ARGS[
                "ipv6" if address_family == 6 else "ipv4"
            ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        error_log = "bgpq3 exit code is {}".format(process.returncode)
        if err and err.strip():
            error_log += ", stderr: {}".format(err)
        raise ValueError(error_log)

    resolvedobject.extend([p for p in json.loads(out.decode())["object_list"]])

    return resolvedobject

def call_irr_as_set_resolver(irr_as_set, address_family=6):
    """
    Call a subprocess to expand the given AS-SET for the wanted IP version.
    """
    return call_irr_resolver('as_set_prefixes', irr_as_set, address_family)

def call_irr_as_resolver(asn, address_family=6):
    """
    Call a subprocess to get the prefixes for AS for the wanted IP version.
    """
    if not asn:
        return []
    
    # Format the AS-Number to AS<number> for retrieving Prefixes
    if str(asn)[:2] != "AS":
        asstring = "AS{}".format(asn)
    else:
        asstring = asn

    return call_irr_resolver('as_set_prefixes', asstring, address_family)

def call_irr_as_set_to_asn_resolver(irr_as_set, address_family=6):
    """
    Call a subprocess to get all ASNs from an AS-SET for an IP version.
    """
    if not irr_as_set:
        return []

    return call_irr_resolver('as_set_to_asn', irr_as_set, address_family)



def parse_irr_as_set(asn, irr_as_set):
    """
    Validate that an AS-SET is usable and split it into smaller part if it is actually
    composed of several AS-SETs.
    """
    as_sets = []

    # Can't work with empty or whitespace only AS-SET
    if not irr_as_set or not irr_as_set.strip():
        return ["AS{}".format(asn)]

    unparsed = re.split(r"[/,&\s]", irr_as_set)
    for value in unparsed:
        value = value.strip()

        if not value:
            continue

        for regexp in [
            # Remove registry prefix if any
            r"^(?:{}):[:\s]".format(settings.BGPQ3_SOURCES.replace(",", "|")),
            # Removing "ipv4:" and "ipv6:"
            r"^(?:ipv4|ipv6):",
        ]:
            pattern = re.compile(regexp, flags=re.IGNORECASE)
            value, number_of_subs_made = pattern.subn("", value)
            # If some substitutions have been made, make sure to clean things up
            if number_of_subs_made > 0:
                value = value.strip()

        as_sets.append(value)

    return as_sets
