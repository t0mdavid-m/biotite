# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

"""
Functions for converting an annotation from/to a GenBank file.
"""

__author__ = "Patrick Kunzmann"
__all__ = ["get_annotation"]

import re
from ....file import InvalidFileError
from ...annotation import Annotation, Feature, Location
from .file import GenBankFile


_KEY_START = 5
_QUAL_START = 21


def get_annotation(gb_file, include_only=None):
    """
    Get the sequence annotation from the *FEATURES* field.
    
    Parameters
    ----------
    include_only : iterable object, optional
        List of names of feature keys (`str`), which should included
        in the annotation. By default all features are included.
    
    Returns
    ----------
    annotation : Annotation
        Sequence annotation from the file.
    """
    fields = gb_file.get_fields("FEATURES")
    if len(fields) == 0:
        raise InvalidFileError("File has no 'FEATURES' field")
    if len(fields) > 1:
        raise InvalidFileError("File has multiple 'FEATURES' fields")
    lines, _ = fields[0]
    
    # Parse all lines to create an index of features
    feature_list = []
    feature_key = None
    feature_value = ""
    for line in lines:
        # Check if line contains feature key
        if line[_KEY_START] != " ":
            if feature_key is not None:
                # Store old feature key and value
                feature_list.append((feature_key, feature_value))
            # Track new key
            feature_key = line[_KEY_START : _QUAL_START-1].strip()
            feature_value = ""
        feature_value += line[_QUAL_START:] + " "
    # Store last feature key and value (loop already exited)
    feature_list.append((feature_key, feature_value))
    
    # Process only relevant features and put them into Annotation
    annotation = Annotation()
    # Regex to separate qualifiers from each other
    regex = re.compile(r"""(".*?"|/.*?=)""")
    for key, val in feature_list:
        if include_only is None or key in include_only:
            qual_dict = {}
            qualifiers = [s.strip() for s in regex.split(val)]
            # Remove empty quals
            qualifiers = [s for s in qualifiers if s]
            # First string is location identifier
            loc_string = qualifiers.pop(0).strip()
            try:
                locs = _parse_locs(loc_string)
            except:
                raise InvalidFileError(
                    f"'{loc_string}' is an invalid location identifier"
                )
            qual_key = None
            qual_val = None
            for qual in qualifiers:
                if qual[0] == "/":
                    # Store previous qualifier pair
                    if qual_key is not None:
                        # In case of e.g. '/pseudo'
                        # 'qual_val' is 'None'
                        _set_qual(qual_dict, qual_key, qual_val)
                        qual_key = None
                        qual_val = None
                    # Qualifier key
                    # -> remove "/" and "="
                    qual_key = qual[1:-1]
                else:
                    # Qualifier value
                    # -> remove potential quotes
                    if qual[0] == '"':
                        qual_val = qual[1:-1]
                    else:
                        qual_val = qual
            # Store final qualifier pair
            if qual_key is not None:
                _set_qual(qual_dict, qual_key, qual_val)
            annotation.add_feature(Feature(key, locs, qual_dict))
    return annotation


def _parse_locs(loc_str):
    locs = []
    if loc_str.startswith(("join", "order")):
        str_list = loc_str[loc_str.index("(")+1:loc_str.rindex(")")].split(",")
        for s in str_list:
            locs.extend(_parse_locs(s))
    elif loc_str.startswith("complement"):
        compl_str = loc_str[loc_str.index("(")+1:loc_str.rindex(")")]
        compl_locs = [
            Location(loc.first, loc.last, Location.Strand.REVERSE, loc.defect) 
            for loc in _parse_locs(compl_str)
        ]
        locs.extend(compl_locs)
    else:
        locs = [_parse_single_loc(loc_str)]
    return locs


def _parse_single_loc(loc_str):
    if ".." in loc_str:
        split_char = ".."
        defect = Location.Defect.NONE
    elif "." in loc_str:
        split_char = "."
        defect = Location.Defect.UNK_LOC
    elif "^" in loc_str:
        split_char = "^"
        loc_str_split = loc_str.split("..")
        defect = Location.Defect.BETWEEN
    else:
        # Parse single location
        defect = Location.Defect.NONE
        if loc_str[0] == "<":
            loc_str = loc_str[1:]
            defect |= Location.Defect.BEYOND_LEFT
        elif loc_str[0] == ">":
            loc_str = loc_str[1:]
            defect |= Location.Defect.BEYOND_RIGHT
        first_and_last = int(loc_str)
        return Location(first_and_last, first_and_last, defect=defect)
    # Parse location range
    loc_str_split = loc_str.split(split_char)
    first_str = loc_str_split[0]
    last_str = loc_str_split[1]
    # Parse Defects
    if first_str[0] == "<":
        first = int(first_str[1:])
        defect |= Location.Defect.BEYOND_LEFT
    else:
        first = int(first_str)
    if last_str[0] == ">":
        last = int(last_str[1:])
        defect |= Location.Defect.BEYOND_RIGHT
    else:
        last = int(last_str)
    return Location(first, last, defect=defect)


def _set_qual(qual_dict, key, val):
    """
    Set a mapping key to val in the dictionary.
    If the key already exists in the dictionary, append the value (str)
    to the existing value, separated by a line break
    """
    if key in qual_dict:
        qual_dict[key] += "\n" + val
    else:
        qual_dict[key] = val