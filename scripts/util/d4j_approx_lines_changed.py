import os
import re
import sys

from os.path import abspath

D4J = abspath('../../analyzers/defects4j/framework/projects')
OUTPUT_DIR = abspath('../auxiliary-data')

class GitHubPatch:
    def __init__(self, image_tag, filename, patch_lower, patch_upper):
        self.image_tag = image_tag
        self.filename = filename
        self.patch_lower = patch_lower
        self.patch_upper = patch_upper

    def to_CSV(self):
        return '{},{},{},{}'.format(self.image_tag, self.filename, self.patch_lower, self.patch_upper)

def main(argv=None):
    argv = argv or sys.argv

    image_tag_file = _validate_input(argv)
    patch_list = []
    with open(image_tag_file) as file:
        for image_tag in file:
            image_tag = image_tag.strip()
            project, num_id = image_tag.split('-')
            try:
                file_ranges = _get_files_changed(project, num_id)
                patch_list = patch_list + _create_GitHubPatch_list(image_tag, file_ranges)
            except:
                continue

    with open(os.path.join(OUTPUT_DIR, 'code-diff.csv'), 'a') as file:
        for patch in patch_list:
            file.write(patch.to_CSV() + '\n')


def _get_range(sub_line, sub_range, add_line, add_range):
    # Catches @@ -2,5 +2,6 @@
    if sub_line and sub_range and add_line and add_range:
        sub_line, sub_range, add_line, add_range = int(sub_line), int(sub_range), int(add_line), int(add_range)
    # Catches @@ -0,0 +1 @@
    elif sub_line and sub_range and add_line and add_range is None:
    # elif sub_line and sub_range and add_line and not add_range:
        sub_line, sub_range, add_line, add_range = int(sub_line), int(sub_range), int(add_line), 0
    # Catches @@ -1 +1,2 @@
    elif sub_line and sub_range is None and add_line and add_range:
        sub_line, sub_range, add_line, add_range = int(sub_line), 0, int(add_line), int(add_range)
    # Catches @@ -1 +1 @@
    elif sub_line and sub_range is None and add_line and add_range is None:
        sub_line, sub_range, add_line, add_range = int(sub_line), 0, int(add_line), 0
    
    if sub_line < add_line:
        range_lower = sub_line
        range_upper = add_line + add_range
    elif sub_line > add_line:
        range_lower = add_line
        range_upper = sub_line + sub_range
    else: # sub_line == add_line
        range_lower = add_line
        range_upper = add_line + max(sub_range, add_range)

    return range_lower, range_upper


def _get_files_changed(project, num_id):

    src_fp = '{}/{}/patches/{}.src.patch'.format(D4J, project, num_id)
    test_fp = '{}/{}/patches/{}.test.patch'.format(D4J, project, num_id)
    file_ranges = {}
    fn_count = 0
    fn_map = {}
    file_lines = []
    for x in [src_fp, test_fp]:
        with open(x) as f:
            file_lines = [*file_lines, *[line.strip() for line in f.readlines()]]
    for line in file_lines:
        match_obj = re.search(r'--- (.+)', line, re.M)
        if match_obj:
            file_line = match_obj.group(1).split('/')
            fn = file_line[len(file_line) - 1]
            file_ranges[fn] = []
            fn_map[fn_count] = fn
            fn_count += 1
    count = 0
    for i in range(1):
        #file_ranges[x['filename']] = []
        range_lower, range_upper = 0, 0
        sub = 0
        add = 0
        #if 'patch' in x:
        if True:
            for line in file_lines:
                line = line.strip()
                if count >= fn_count:
                    break;
                if line is None:
                    contune
                match_obj = re.search(r'^@@ -([0-9]+),?([0-9]+)? \+([0-9]+),?([0-9]+)? @@', line, re.M)
                if match_obj:
                    #if sub != 0 or add != 0:
                    #    print(line)
                    #file_ranges[fn_map[count]].append((range_lower, range_upper))
                    range_lower, range_upper = _get_range(match_obj.group(1), match_obj.group(2), match_obj.group(3), match_obj.group(4))
                    add = 0
                    file_ranges[fn_map[count]].append((range_lower, range_upper))
                    count += 1
                    sub = 0
                    continue
                match_obj = re.search(r'^(\+).*', line, re.M)
                if match_obj:
                    add = add + 1
                    continue
                match_obj = re.search(r'^(-).*', line, re.M)
                if match_obj:
                    sub = sub + 1
                    continue

            #if sub != 0 or add != 0:
            #file_ranges[x['filename']].append((range_lower, range_upper))
            #    file_ranges[fn_map[count-1]].append((range_lower, range_upper))

    return file_ranges


def _create_GitHubPatch_list(image_tag, files_changed_list):
    patch_list = []
    for key in files_changed_list:
        for patch in files_changed_list[key]:
            range_lower, range_upper = patch[0], patch[1]
            patch_list.append(GitHubPatch(image_tag, key, range_lower, range_upper))
    return patch_list


def _print_usage():
    print('Usage: python3 approx_lines_changed.py <image_tag_filepath>')
    print('image_tag_filepath: The filepath to the new-line separated file containing image-tags')


def _validate_input(argv):
    if len(argv) != 2:
        _print_usage()
        sys.exit(1)
    image_tag_file = argv[1]

    return image_tag_file


if __name__ == '__main__':
    sys.exit(main())
