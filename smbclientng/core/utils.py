#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : utils.py
# Author             : Podalirius (@podalirius_)
# Date created       : 23 may 2024


import datetime
import os
import ntpath
import re
import stat


def parse_lm_nt_hashes(lm_nt_hashes_string):
    """
    Parse the input string containing LM and NT hash values and return them separately.

    This function takes a string containing LM and NT hash values, typically separated by a colon (:).
    It returns the LM and NT hash values as separate strings. If only one hash value is provided, it is
    assumed to be the NT hash and the LM hash is set to its default value. If no valid hash values are
    found, both return values are empty strings.

    Args:
        lm_nt_hashes_string (str): A string containing LM and NT hash values separated by a colon.

    Returns:
        tuple: A tuple containing two strings (lm_hash_value, nt_hash_value).
               - lm_hash_value: The LM hash value or its default if not provided.
               - nt_hash_value: The NT hash value or its default if not provided.
    
    Extracted from p0dalirius/sectools library
    Src: https://github.com/p0dalirius/sectools/blob/7bb3f5cb7815ad4d4845713c8739e2e2b0ea4e75/sectools/windows/crypto.py#L11-L24
    """

    lm_hash_value, nt_hash_value = "", ""
    if lm_nt_hashes_string is not None:
        matched = re.match("([0-9a-f]{32})?(:)?([0-9a-f]{32})?", lm_nt_hashes_string.strip().lower())
        m_lm_hash, m_sep, m_nt_hash = matched.groups()
        if m_lm_hash is None and m_sep is None and m_nt_hash is None:
            lm_hash_value, nt_hash_value = "", ""
        elif m_lm_hash is None and m_nt_hash is not None:
            lm_hash_value = "aad3b435b51404eeaad3b435b51404ee"
            nt_hash_value = m_nt_hash
        elif m_lm_hash is not None and m_nt_hash is None:
            lm_hash_value = m_lm_hash
            nt_hash_value = "31d6cfe0d16ae931b73c59d7e0c089c0"
    return lm_hash_value, nt_hash_value


def b_filesize(l):
    """
    Convert a file size from bytes to a more readable format using the largest appropriate unit.

    This function takes an integer representing a file size in bytes and converts it to a human-readable
    string using the largest appropriate unit from bytes (B) to petabytes (PB). The result is rounded to
    two decimal places.

    Args:
        l (int): The file size in bytes.

    Returns:
        str: A string representing the file size in a more readable format, including the appropriate unit.
    """

    units = ['B','kB','MB','GB','TB','PB']
    for k in range(len(units)):
        if l < (1024**(k+1)):
            break
    return "%4.2f %s" % (round(l/(1024**(k)),2), units[k])


def unix_permissions(entryname):
    """
    Generate a string representing the Unix-style permissions for a given file or directory.

    This function uses the os.lstat() method to retrieve the status of the specified file or directory,
    then constructs a string that represents the Unix-style permissions based on the mode of the file.

    Args:
        entryname (str): The path to the file or directory for which permissions are being determined.

    Returns:
        str: A string of length 10 representing the Unix-style permissions (e.g., '-rwxr-xr--').
             The first character is either 'd' (directory), '-' (not a directory), followed by
             three groups of 'r', 'w', 'x' (read, write, execute permissions) for owner, group,
             and others respectively.
    """

    mode = os.lstat(entryname).st_mode
    permissions = []

    permissions.append('d' if stat.S_ISDIR(mode) else '-')

    permissions.append('r' if mode & stat.S_IRUSR else '-')
    permissions.append('w' if mode & stat.S_IWUSR else '-')
    permissions.append('x' if mode & stat.S_IXUSR else '-')

    permissions.append('r' if mode & stat.S_IRGRP else '-')
    permissions.append('w' if mode & stat.S_IWGRP else '-')
    permissions.append('x' if mode & stat.S_IXGRP else '-')

    permissions.append('r' if mode & stat.S_IROTH else '-')
    permissions.append('w' if mode & stat.S_IWOTH else '-')
    permissions.append('x' if mode & stat.S_IXOTH else '-')

    return ''.join(permissions)


def STYPE_MASK(stype_value):
    """
    Extracts the share type flags from a given share type value.

    This function uses bitwise operations to determine which share type flags are set in the provided `stype_value`.
    It checks against known share type flags and returns a list of the flags that are set.

    Parameters:
        stype_value (int): The share type value to analyze, typically obtained from SMB share properties.

    Returns:
        list: A list of strings, where each string represents a share type flag that is set in the input value.
    """

    known_flags = {
        ## One of the following values may be specified. You can isolate these values by using the STYPE_MASK value.
        # Disk drive.
        "STYPE_DISKTREE": 0x0,

        # Print queue.
        "STYPE_PRINTQ": 0x1,

        # Communication device.
        "STYPE_DEVICE": 0x2,

        # Interprocess communication (IPC).
        "STYPE_IPC": 0x3,

        ## In addition, one or both of the following values may be specified.
        # Special share reserved for interprocess communication (IPC$) or remote administration of the server (ADMIN$).
        # Can also refer to administrative shares such as C$, D$, E$, and so forth. For more information, see Network Share Functions.
        "STYPE_SPECIAL": 0x80000000,

        # A temporary share.
        "STYPE_TEMPORARY": 0x40000000
    }
    flags = []
    if (stype_value & 0b11) == known_flags["STYPE_DISKTREE"]:
        flags.append("STYPE_DISKTREE")
    elif (stype_value & 0b11) == known_flags["STYPE_PRINTQ"]:
        flags.append("STYPE_PRINTQ")
    elif (stype_value & 0b11) == known_flags["STYPE_DEVICE"]:
        flags.append("STYPE_DEVICE")
    elif (stype_value & 0b11) == known_flags["STYPE_IPC"]:
        flags.append("STYPE_IPC")
    if (stype_value & known_flags["STYPE_SPECIAL"]) == known_flags["STYPE_SPECIAL"]:
        flags.append("STYPE_SPECIAL")
    if (stype_value & known_flags["STYPE_TEMPORARY"]) == known_flags["STYPE_TEMPORARY"]:
        flags.append("STYPE_TEMPORARY")
    return flags


def windows_ls_entry(entry, config, pathToPrint=None):
    """
    This function generates a metadata string based on the attributes of the provided entry object.
    
    Parameters:
        entry (object): An object representing a file or directory entry.

    Returns:
        str: A string representing the metadata of the entry, including attributes like directory, archive, compressed, hidden, normal, readonly, system, and temporary.
    """
    
    if pathToPrint is not None:
        pathToPrint = pathToPrint + ntpath.sep + entry.get_longname()
    else:
        pathToPrint = entry.get_longname()

    meta_string = ""
    meta_string += ("d" if entry.is_directory() else "-")
    meta_string += ("a" if entry.is_archive() else "-")
    meta_string += ("c" if entry.is_compressed() else "-")
    meta_string += ("h" if entry.is_hidden() else "-")
    meta_string += ("n" if entry.is_normal() else "-")
    meta_string += ("r" if entry.is_readonly() else "-")
    meta_string += ("s" if entry.is_system() else "-")
    meta_string += ("t" if entry.is_temporary() else "-")

    size_str = b_filesize(entry.get_filesize())

    date_str = datetime.datetime.fromtimestamp(entry.get_atime_epoch()).strftime("%Y-%m-%d %H:%M")
    
    if entry.is_directory():
        if config.no_colors:
            print("%s %10s  %s  %s\\" % (meta_string, size_str, date_str, pathToPrint))
        else:
            print("%s %10s  %s  \x1b[1;96m%s\x1b[0m\\" % (meta_string, size_str, date_str, pathToPrint))
    else:
        if config.no_colors:
            print("%s %10s  %s  %s" % (meta_string, size_str, date_str, pathToPrint))
        else:
            print("%s %10s  %s  \x1b[1m%s\x1b[0m" % (meta_string, size_str, date_str, pathToPrint))


def local_tree(path, config):
    """
    This function recursively lists the contents of a directory in a tree-like format.

    Parameters:
        path (str): The path to the directory to list.
        config (object): Configuration settings which may affect the output, such as whether to use colors.

    Returns:
        None: This function does not return anything but prints the directory tree to the console.
    """

    def recurse_action(base_dir="", path=[], prompt=[]):
        bars = ["│   ", "├── ", "└── "]

        local_path = os.path.normpath(base_dir + os.path.sep + os.path.sep.join(path) + os.path.sep)

        entries = []
        try:
            entries = os.listdir(local_path)
        except Exception as err:
            if config.no_colors:
                print("%s%s" % (''.join(prompt+[bars[2]]), err))
            else:
                print("%s\x1b[1;91m%s\x1b[0m" % (''.join(prompt+[bars[2]]), err))
            return 

        entries = sorted(entries)

        # 
        if len(entries) > 1:
            index = 0
            for entry in entries:
                index += 1
                # This is the first entry 
                if index == 0:
                    if os.path.isdir(local_path + os.path.sep + entry):
                        if config.no_colors:
                            print("%s%s%s" % (''.join(prompt+[bars[1]]), entry, os.path.sep))
                        else:
                            print("%s\x1b[1;96m%s\x1b[0m%s" % (''.join(prompt+[bars[1]]), entry, os.path.sep))
                        recurse_action(
                            base_dir=base_dir, 
                            path=path+[entry],
                            prompt=prompt+["│   "]
                        )
                    else:
                        if config.no_colors:
                            print("%s%s" % (''.join(prompt+[bars[1]]), entry))
                        else:
                            print("%s\x1b[1m%s\x1b[0m" % (''.join(prompt+[bars[1]]), entry))

                # This is the last entry
                elif index == len(entries):
                    if os.path.isdir(local_path + os.path.sep + entry):
                        if config.no_colors:
                            print("%s%s%s" % (''.join(prompt+[bars[2]]), entry, os.path.sep))
                        else:
                            print("%s\x1b[1;96m%s\x1b[0m%s" % (''.join(prompt+[bars[2]]), entry, os.path.sep))
                        recurse_action(
                            base_dir=base_dir, 
                            path=path+[entry],
                            prompt=prompt+["    "]
                        )
                    else:
                        if config.no_colors:
                            print("%s%s" % (''.join(prompt+[bars[2]]), entry))
                        else:
                            print("%s\x1b[1m%s\x1b[0m" % (''.join(prompt+[bars[2]]), entry))
                    
                # These are entries in the middle
                else:
                    if os.path.isdir(local_path + os.path.sep + entry):
                        if config.no_colors:
                            print("%s%s%s" % (''.join(prompt+[bars[1]]), entry, os.path.sep))
                        else:
                            print("%s\x1b[1;96m%s\x1b[0m%s" % (''.join(prompt+[bars[1]]), entry, os.path.sep))
                        recurse_action(
                            base_dir=base_dir, 
                            path=path+[entry],
                            prompt=prompt+["│   "]
                        )
                    else:
                        if config.no_colors:
                            print("%s%s" % (''.join(prompt+[bars[1]]), entry))
                        else:
                            print("%s\x1b[1m%s\x1b[0m" % (''.join(prompt+[bars[1]]), entry))

        # 
        elif len(entries) == 1:
            entry = entries[0]
            if os.path.isdir(local_path + os.path.sep + entry):
                if config.no_colors:
                    print("%s%s%s" % (''.join(prompt+[bars[2]]), entry, os.path.sep))
                else:
                    print("%s\x1b[1;96m%s\x1b[0m%s" % (''.join(prompt+[bars[2]]), entry, os.path.sep))
                recurse_action(
                    base_dir=base_dir, 
                    path=path+[entry],
                    prompt=prompt+["    "]
                )
            else:
                if config.no_colors:
                    print("%s%s" % (''.join(prompt+[bars[2]]), entry))
                else:
                    print("%s\x1b[1m%s\x1b[0m" % (''.join(prompt+[bars[2]]), entry))

    # Entrypoint
    try:
        if config.no_colors:
            print("%s%s" % (path, os.path.sep))
        else:
            print("\x1b[1;96m%s\x1b[0m%s" % (path, os.path.sep))
        recurse_action(
            base_dir=os.getcwd(),
            path=[path],
            prompt=[""]
        )
    except (BrokenPipeError, KeyboardInterrupt) as e:
        print("[!] Interrupted.")

