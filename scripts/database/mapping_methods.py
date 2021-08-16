'''
Contains functions for generating the different database queries for
each respective mapping method.
'''

def generate_code_diff_query(diff_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{diff_table}` INNER JOIN `{tool_table}` ON ' \
           '`{diff_table}`.image_tag = `{tool_table}`.image_tag WHERE ' \
           '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND ' \
           'LOCATE(`{diff_table}`.file,`{tool_table}`.file) != "" or '  \
           'LOCATE(`{tool_table}`.file,`{diff_table}`.file) != "" AND ' \
           '(((`{tool_table}`.bug_lower BETWEEN `{diff_table}`.patch_lower AND ' \
           '`{diff_table}`.patch_upper) OR (`{tool_table}`.bug_upper BETWEEN ' \
           '`{diff_table}`.patch_lower AND `{diff_table}`.patch_upper)) OR ' \
           '((`{diff_table}`.patch_lower BETWEEN `{tool_table}`.bug_lower AND ' \
           '`{tool_table}`.bug_upper) OR (`{diff_table}`.patch_lower BETWEEN ' \
           '`{tool_table}`.bug_lower AND `{tool_table}`.bug_upper)));'.format(**{
                'diff_table': diff_table,
                'tool_table': tool_table,
            })


def generate_code_diff_query_infer(diff_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{diff_table}` INNER JOIN `{tool_table}` ON ' \
           '`{diff_table}`.image_tag = `{tool_table}`.image_tag WHERE ' \
           '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND ' \
           '`{tool_table}`.bug_type = "NULL_DEREFERENCE" AND ' \
           'LOCATE(`{diff_table}`.file,`{tool_table}`.file) != "" or '  \
           'LOCATE(`{tool_table}`.file,`{diff_table}`.file) != "" AND ' \
           '(((`{tool_table}`.bug_lower BETWEEN `{diff_table}`.patch_lower AND ' \
           '`{diff_table}`.patch_upper) OR (`{tool_table}`.bug_upper BETWEEN ' \
           '`{diff_table}`.patch_lower AND `{diff_table}`.patch_upper)) OR ' \
           '((`{diff_table}`.patch_lower BETWEEN `{tool_table}`.bug_lower AND ' \
           '`{tool_table}`.bug_upper) OR (`{diff_table}`.patch_lower BETWEEN ' \
           '`{tool_table}`.bug_lower AND `{tool_table}`.bug_upper)));'.format(**{
                'diff_table': diff_table,
                'tool_table': tool_table,
            })


def generate_code_diff_query_spotbugs(diff_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{diff_table}` INNER JOIN `{tool_table}` ON ' \
           '`{diff_table}`.image_tag = `{tool_table}`.image_tag WHERE ' \
           '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND ' \
           'LOCATE( "NP_",`{tool_table}`.bug_type) != "" AND ' \
           'LOCATE(`{diff_table}`.file,`{tool_table}`.file) != "" or '  \
           'LOCATE(`{tool_table}`.file,`{diff_table}`.file) != "" AND ' \
           '(((`{tool_table}`.bug_lower BETWEEN `{diff_table}`.patch_lower AND ' \
           '`{diff_table}`.patch_upper) OR (`{tool_table}`.bug_upper BETWEEN ' \
           '`{diff_table}`.patch_lower AND `{diff_table}`.patch_upper)) OR ' \
           '((`{diff_table}`.patch_lower BETWEEN `{tool_table}`.bug_lower AND ' \
           '`{tool_table}`.bug_upper) OR (`{diff_table}`.patch_lower BETWEEN ' \
           '`{tool_table}`.bug_lower AND `{tool_table}`.bug_upper)));'.format(**{
                'diff_table': diff_table,
                'tool_table': tool_table,
            })


def generate_code_diff_query_infer(diff_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{diff_table}` INNER JOIN `{tool_table}` ON ' \
           '`{diff_table}`.image_tag = `{tool_table}`.image_tag WHERE ' \
           '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND ' \
           '`{tool_table}`.bug_type = "NULL_DEREFERENCE" AND ' \
           'LOCATE(`{diff_table}`.file,`{tool_table}`.file) != "" or '  \
           'LOCATE(`{tool_table}`.file,`{diff_table}`.file) != "" AND ' \
           '(((`{tool_table}`.bug_lower BETWEEN `{diff_table}`.patch_lower AND ' \
           '`{diff_table}`.patch_upper) OR (`{tool_table}`.bug_upper BETWEEN ' \
           '`{diff_table}`.patch_lower AND `{diff_table}`.patch_upper)) OR ' \
           '((`{diff_table}`.patch_lower BETWEEN `{tool_table}`.bug_lower AND ' \
           '`{tool_table}`.bug_upper) OR (`{diff_table}`.patch_lower BETWEEN ' \
           '`{tool_table}`.bug_lower AND `{tool_table}`.bug_upper)));'.format(**{
                'diff_table': diff_table,
                'tool_table': tool_table,
            })


def generate_covered_lines_query(covered_lines_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{covered_lines_table}` INNER JOIN `{tool_table}` ON ' \
           '`{covered_lines_table}`.image_tag = `{tool_table}`.image_tag WHERE ' \
           'LOCATE(`{covered_lines_table}`.file,`{tool_table}`.file) != "" AND ' \
           '(((`{tool_table}`.bug_lower BETWEEN `{covered_lines_table}`.line AND ' \
           '`{covered_lines_table}`.line) OR (`{tool_table}`.bug_upper BETWEEN ' \
           '`{covered_lines_table}`.line AND `{covered_lines_table}`.line)) OR ' \
           '((`{covered_lines_table}`.line BETWEEN `{tool_table}`.bug_lower AND ' \
           '`{tool_table}`.bug_upper) OR (`{covered_lines_table}`.line BETWEEN ' \
           '`{tool_table}`.bug_lower AND `{tool_table}`.bug_upper)));'.format(**{
                'covered_lines_table': covered_lines_table,
                'tool_table': tool_table,
            })


def generate_covered_lines_original_query_infer(covered_lines_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{tool_table}` INNER JOIN `{covered_lines_table}` ON ' \
    '`{tool_table}`.image_tag = `{covered_lines_table}`.image_tag AND '\
    '`{covered_lines_table}`.line = `{tool_table}`.bug_upper AND ' \
    '`{covered_lines_table}`.line = `{tool_table}`.bug_lower AND ' \
    '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND (LOCATE(`{covered_lines_table}`.file,`{tool_table}`.file) != "" OR LOCATE(`{tool_table}`.file, `{covered_lines_table}`.file) != "") AND `{tool_table}`.bug_type = "NULL_DEREFERENCE";'.format(**{
                'covered_lines_table': covered_lines_table,
                'tool_table': tool_table,
    })


def generate_covered_lines_original_query(covered_lines_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{tool_table}` INNER JOIN `{covered_lines_table}` ON ' \
    '`{tool_table}`.image_tag = `{covered_lines_table}`.image_tag AND '\
    '`{covered_lines_table}`.line = `{tool_table}`.bug_upper AND ' \
    '`{covered_lines_table}`.line = `{tool_table}`.bug_lower AND ' \
    '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND (LOCATE(`{covered_lines_table}`.file,`{tool_table}`.file) != "" OR LOCATE(`{tool_table}`.file, `{covered_lines_table}`.file) != "");'.format(**{
                'covered_lines_table': covered_lines_table,
                'tool_table': tool_table,
    })


def generate_covered_lines_original_query_spotbugs(covered_lines_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{tool_table}` INNER JOIN `{covered_lines_table}` ON ' \
    '`{tool_table}`.image_tag = `{covered_lines_table}`.image_tag AND '\
    '`{covered_lines_table}`.line = `{tool_table}`.bug_upper AND ' \
    '`{covered_lines_table}`.line = `{tool_table}`.bug_lower AND ' \
    '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND (LOCATE(`{covered_lines_table}`.file,`{tool_table}`.file) != "" OR LOCATE(`{tool_table}`.file, `{covered_lines_table}`.file) != "") AND LOCATE( "NP_",`{tool_table}`.bug_type) != "";'.format(**{
                'covered_lines_table': covered_lines_table,
                'tool_table': tool_table,
    })


def generate_stack_trace_query(stack_trace_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{stack_trace_table}` INNER JOIN `{tool_table}` ON ' \
           '`{stack_trace_table}`.image_tag = `{tool_table}`.image_tag WHERE ' \
           'LOCATE(`{stack_trace_table}`.file,`{tool_table}`.file) != "" AND ' \
           '(((`{tool_table}`.bug_lower BETWEEN `{stack_trace_table}`.line AND ' \
           '`{stack_trace_table}`.line) OR (`{tool_table}`.bug_upper BETWEEN ' \
           '`{stack_trace_table}`.line AND `{stack_trace_table}`.line)) OR ' \
           '((`{stack_trace_table}`.line BETWEEN `{tool_table}`.bug_lower AND ' \
           '`{tool_table}`.bug_upper) OR (`{stack_trace_table}`.line BETWEEN ' \
           '`{tool_table}`.bug_lower AND `{tool_table}`.bug_upper)));'.format(**{
                'stack_trace_table': stack_trace_table,
                'tool_table': tool_table,
            })


def generate_stack_trace_original_query_infer(stack_trace_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{tool_table}` INNER JOIN `{stack_trace_table}` ON ' \
    '`{tool_table}`.image_tag = `{stack_trace_table}`.image_tag AND '\
    '`{stack_trace_table}`.line = `{tool_table}`.bug_upper AND ' \
    '`{stack_trace_table}`.line = `{tool_table}`.bug_lower AND ' \
    '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND (LOCATE(`{stack_trace_table}`.file,`{tool_table}`.file) != "" OR LOCATE(`{tool_table}`.file, `{stack_trace_table}`.file) != "") AND `{tool_table}`.bug_type = "NULL_DEREFERENCE";'.format(**{
                'stack_trace_table': stack_trace_table,
                'tool_table': tool_table,
    })


def generate_stack_trace_original_query(stack_trace_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{tool_table}` INNER JOIN `{stack_trace_table}` ON ' \
    '`{tool_table}`.image_tag = `{stack_trace_table}`.image_tag AND '\
    '`{stack_trace_table}`.line = `{tool_table}`.bug_upper AND ' \
    '`{stack_trace_table}`.line = `{tool_table}`.bug_lower AND ' \
    '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND (LOCATE(`{stack_trace_table}`.file,`{tool_table}`.file) != "" OR LOCATE(`{tool_table}`.file, `{stack_trace_table}`.file) != "");'.format(**{
                'stack_trace_table': stack_trace_table,
                'tool_table': tool_table,
    })


def generate_stack_trace_original_query_spotbugs(stack_trace_table: str, tool_table: str) -> str:
    return 'SELECT * FROM `{tool_table}` INNER JOIN `{stack_trace_table}` ON ' \
    '`{tool_table}`.image_tag = `{stack_trace_table}`.image_tag AND '\
    '`{stack_trace_table}`.line = `{tool_table}`.bug_upper AND ' \
    '`{stack_trace_table}`.line = `{tool_table}`.bug_lower AND ' \
    '(`{tool_table}`.version = "failed" OR `{tool_table}`.version = "b") AND (LOCATE(`{stack_trace_table}`.file,`{tool_table}`.file) != "" OR LOCATE(`{tool_table}`.file, `{stack_trace_table}`.file) != "") AND LOCATE( "NP_",`{tool_table}`.bug_type) != "";'.format(**{
                'stack_trace_table': stack_trace_table,
                'tool_table': tool_table,
    })


def generate_report_diff_query(tool_table: str) -> str:
    return """SELECT f.image_tag
from(SELECT image_tag, count(*) as count FROM `{tool_table}` where (version = 'failed' or version = 'b') group by image_tag) f
LEFT OUTER join (SELECT image_tag, count(*) as count FROM `{tool_table}` where (version = 'passed' or version = 'f') group by image_tag) p
on f.image_tag = p.image_tag
WHERE (f.count > p.count) OR (p.count IS NULL)
;""".format(**{
    'tool_table': tool_table})


def generate_report_diff_query_infer(tool_table: str) -> str:
    return """SELECT f.image_tag
from(SELECT image_tag, count(*) as count FROM `{tool_table}` where (version = 'failed' or version = 'b') AND bug_type = 'NULL_DEREFERENCE' group by image_tag) f
LEFT OUTER join (SELECT image_tag, count(*) as count FROM `{tool_table}` where (version = 'passed' or version = 'f') AND bug_type = 'NULL_DEREFERENCE' group by image_tag) p
on f.image_tag = p.image_tag
WHERE (f.count > p.count) OR (p.count IS NULL)
;""".format(**{
    'tool_table': tool_table})


def generate_report_diff_query_spotbugs(tool_table: str) -> str:
    return """SELECT f.image_tag
from(SELECT image_tag, count(*) as count FROM `{tool_table}` where (version = 'failed' or version = 'b') AND LOCATE( 'NP_', bug_type) != '' group by image_tag) f
LEFT OUTER join (SELECT image_tag, count(*) as count FROM `{tool_table}` where (version = 'passed' or version = 'f') AND LOCATE( 'NP_', bug_type) != '' group by image_tag) p
on f.image_tag = p.image_tag
WHERE (f.count > p.count) OR (p.count IS NULL)
;""".format(**{
    'tool_table': tool_table})
