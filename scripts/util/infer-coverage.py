"""
Checks if all source and test files were analyzed by infer.
Run this script in the same directory with ./infer-out
    and all src/test dirs.
"""
import re
import os
import sys
from os.path import join


def add_arr_and_dict_to_list(files_list, array, dictionary):
    """
    Populates an empty list with an array and a dictionary
    Args:
        files_list: empty list
        array: contains file paths
        dictionary: contains file names &
                    how many times they appear
    Returns:
        A list containing array and dictionary
    """
    files_list.append(array)
    files_list.append(dictionary)
    return files_list


def add_file_to_dict(dictionary, file):
    """
    Populates a dictionary with
        key: file name
        value: number of instances in the  directory
    Args:
        dictionary: dictionary of file names
        file: file name to be added to dictionary
    Returns:
        The modified dictionary
    """
    # If file exists in dictionary
    if file in dictionary:
        # Add number of instances of the file
        dictionary[file] += 1
    # If file does not exist
    else:
        # Add it to our dictionary
        dictionary[file] = 1
    return dictionary


def cut_last_three_fields(filename):
    """
    Cut the last three fields of child HTML files
        to retrieve the rest of the filename
    Args:
        filename: full filename
    Returns:
        The modified filename
    Filename format: path.filename.method(args):return.hashcode.ext
    For example, if we have the string:
    org.sbolstandard.core.fileName$.method(type arg1):void.1234a.html
        1) path                           = org.sbolstandard.core
        2) .filename.method(args):return. = .fileName$.method(type arg1):void.
        3) hashcode.                      = 1234a.
        4) ext                            = html
    """
    regex = "([a-z0-9._]+)" \
            "([.][a-zA-Z0-9_$,:;<>.()\[\]-]+\.)" \
            "([a-z0-9]+\.)" \
            "([a-z]+)"
    fname = re.match(regex, filename)
    # Return the path field
    return fname.groups()[0]


def get_filename(directory_path):
    """
    For ./infer-out/captured directories with no child HTML
        get its filename from directory path
    Args:
        directory_path: path to a directory
                        with no child HTML
    Returns:
        The modified filename
    """
    # Get file.java.hashcode from dir1/dir2/file.java.hashcode
    fields = directory_path.split("/")
    # Get file.java from filename.java.hashcode
    filename_parts = fields[3].split(".")
    filename = filename_parts[0] + "." + filename_parts[1]

    return filename


def get_filename_from_dir(directory_path):
    """
    Retrieves a filename from a directory path
    e.g. we want to get filename from
         ./infer-out/captured/filename.java.hashcode
    Args:
        directory_path: path to a directory
    Returns:
        the filename
    """
    fields = directory_path.split("/")
    filename = fields[3].split(".")
    return filename[0]


def preprocess_infer_files(infer_arr, infer_dic):
    """
    Args:
        infer_arr: empty array
        infer_dic: empty dictionary
    Returns:
        A list containing
            1) populated array of paths of child HTML files
            2) populated dictionary of filenames of dirs
                 w/out child HTML files
    """
    # Traverse through the sub-directories in ./infer-out/captured
    for root, dirs, files in os.walk("./infer-out/captured"):
        for current_directory in dirs:
            directory_path = os.path.join(root, current_directory)

            # Do not enter the "nodes" directory in /captured
            if current_directory == "nodes":
                continue

            # Want to check if current directory has a child HTML file
            has_child_html = False

            # Iterate through the files and directories in current directory
            items = os.listdir(directory_path)

            for item in items:
                # Found a child HTML java file
                if item.endswith(".html"):
                    has_child_html = True
                    # get the path to the filename
                    separated_filename = cut_last_three_fields(item) + "."
                    # append the filename
                    separated_filename += get_filename_from_dir(directory_path)
                    # modify the filename into a valid path
                    final_path = separated_filename.replace(".", "/")
                    infer_arr.append(final_path)
                    break

            # Child HTML not found
            if not has_child_html:
                # Add its filename to captured_dict
                infer_dic = add_file_to_dict(infer_dic,
                                             get_filename(directory_path))

    captured_files_list = []
    captured_files_list = add_arr_and_dict_to_list(captured_files_list,
                                                   infer_arr, infer_dic)
    return captured_files_list


def preprocess_src_and_test_files(src_test_array, src_test_dict):
    """
    Args:
        src_test_array: empty array
        src_test_dict: empty dictionary
    Returns:
        A list containing:
            1) populated array of src and test file paths
            2) populated dictionary of src and test filenames
    """
    # Find all java file paths outside of ./infer-out/captured
    for root, dirs, files in os.walk("."):
        # Ignore any directories within ./infer-out
        if "infer-out" in root:
            continue
        # Check directories outside ./infer-out
        else:
            for dir_name in dirs:
                if "infer-out" not in dir_name:
                    # Make a list of all files outside ./infer-out
                    files = os.listdir(os.path.join(root, dir_name))
                    for file in files:
                        # From the list, get all .java files
                        if file.endswith(".java"):
                            file_path = os.path.join(root, dir_name, file)
                            # Add the file path to src_test_array
                            src_test_array.append(file_path)
                            # Add the filename to src_test_dict
                            java_file = file_path.split("/")[-1]
                            src_test_dict = add_file_to_dict(src_test_dict,
                                                             java_file)

    src_test_list = []
    src_test_list = add_arr_and_dict_to_list(src_test_list,
                                             src_test_array, src_test_dict)
    return src_test_list


def compare_dicts(file, src_test_dict, infer_dict):
    """
    Check if a particular file
        exists in the source/test dict and infer dict
    If file exists, decrement the counter in
        both dictionaries
    Args:
        file: file potentially not analyzed by infer
        src_test_dict: dictionary containing
                       src/test files
        infer_dict: dictionary containing infer files
    Returns:
        True if file exists in both, False otherwise
    """
    if file in src_test_dict and file in infer_dict:
        if src_test_dict[file] > 0 and infer_dict[file] > 0:
            src_test_dict[file] -= 1
            infer_dict[file] -= 1
            return True
    return False


def check_list(not_found_list, src_test_dict, infer_dict):
    """
    Checks a list of files potentially not analyzed by infer
    Verifies if a file was analyzed by infer
        by checking the file in the source/test dict & infer dict
    If the file was indeed analyzed, we remove it from the list
    Args:
        not_found_list: a list of files
        src_test_dict: dictionary containing src/test files
        infer_dict: dictionary containing infer files
    Returns:
        the list of remaining files
    """
    index = 0

    # For each file in not_found_list
    # This loop checks if the list is empty
    while len(not_found_list) > 0 and index < len(not_found_list):
        # Check the file in both src/test and infer dictionaries
        file_found_in_dicts = compare_dicts(not_found_list[index],
                                            src_test_dict, infer_dict)
        # File was found in both src and infer dictionaries
        if file_found_in_dicts:
            # Remove the file from our list
            del not_found_list[index]
        else:  # File was not found in both dictionaries
            # Check the next file on the list
            index += 1

    if len(not_found_list) == 0:
        print("All source and test files were analyzed by infer.")
    else:
        print("These source/test files were not analyzed"
              " by infer: {}".format(not_found_list))

    return not_found_list


def compare_arrays(not_found_list, src_test_array, infer_array):
    """
    Compare source and test files with those analyzed by infer
    If arrays differ, return a list of files not analyzed
    Args:
        not_found_list: list of files not analyzed by infer
        src_test_array: source and test files
        infer_array: files analyzed by infer
    Returns:
        list of files
    """
    file_found = False

    # For each source and test file
    for src_test_path in src_test_array:
        # Find a corresponding file in the infer array
        for infer_path in infer_array:
            # File is found in infer array
            # (Infer file path is a substring of source/test file path)
            if infer_path in src_test_path:
                file_found = True
                # Move on to the next source/test file
                break

        # File not found in infer array
        if file_found is False:
            # Add file to not_found_list
            filename = src_test_path.split("/")[-1]
            not_found_list.append(filename)

        file_found = False

    return not_found_list


def main():
    """
    Checks if source and test files were analyzed by infer
    If some files were not analyzed,
        this program will print a list of those files
    """
    results = open("results.txt", "w")

    # For the items in ./infer-out/captured
    # Initialize an array for directories with child HTML file
    infer_array = []
    # Initialize a dictionary for directories without a child HTML file
    infer_dict = {}
    # Initialize & fill a list containing the pre-processed infer file path
    # The array contains file paths with a child HTML
    # The dictionary contains file names without a child HTML
    infer_list = preprocess_infer_files(infer_array, infer_dict)
    # Retrieve the infer array and dictionary from infer_list
    infer_array = infer_list[0]
    infer_dict = infer_list[1]

    # Initialize an array and dictionary for all src and test files
    src_and_test_array = []
    src_and_test_dict = {}
    # Gather ALL the java src and test file paths and file names
    # The array keeps file paths, the dictionary keeps file names
    src_and_test_list = preprocess_src_and_test_files(src_and_test_array,
                                                      src_and_test_dict)
    # Retrieve the array and dictionary from the list
    src_and_test_array = src_and_test_list[0]
    src_and_test_dict = src_and_test_list[1]

    # Compare arrays
    not_found_list = compare_arrays([], src_and_test_array, infer_array)

    # Prints message: a) all files analyzed OR b) a list of files not analyzed
    not_found_list = check_list(not_found_list, src_and_test_dict, infer_dict)

    if not_found_list:
        for item in not_found_list:
            results.write('{},\n'.format(item))

if __name__ == "__main__":
    sys.exit(main())
