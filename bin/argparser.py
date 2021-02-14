import argparse
import sys

version_tool_this = "dummy"

# message ----------------------------------------------------------------------
class CapitalisedHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = ''
        return super(CapitalisedHelpFormatter, self).add_usage(usage, actions, groups, prefix)


def msg(name=None):
    str_msg = '''
\00
Program: read_counter - a tool to count reads that map to a set of sequences
Version: '''+version_tool_this+'''

Usage: read_counter <command> [options]

Command: map     Map reads to a database and create read count profile
         index   Create a database to use for the 'map' command
         merge   Merge read count profiles to create a table

Type read_counter <command> to print the help for a specific command
        '''
    return str_msg

def print_parse(version_tool):
    global version_tool_this
    version_tool_this = version_tool
    # commands ---------------------------------------------------------------------
    parser = argparse.ArgumentParser(usage=msg(), formatter_class=CapitalisedHelpFormatter,add_help=False)
    #parser = argparse.ArgumentParser(description='This program calculates mOTU-LGs and specI abundances for one sample', add_help = True)
    parser.add_argument('command', action="store", default=None, help='mode to use the mOTU tool',choices=['index','map','merge'])
    # input
    parser.add_argument('-f', action="store", default=None,dest='forwardReads', help='name of input file for reads in forward orientation, fastq formatted, can be gzipped')
    parser.add_argument('-r', action="store", default=None,dest='reverseReads', help='name of input file for reads in reverse orientation, fastq formatted, can be gzipped')
    parser.add_argument('-s', action="store", default=None,dest='singleReads', help='name of input file for reads without mate, fastq formatted, can be gzipped')
    parser.add_argument('-db', action="store", default=None, dest='db', help='database of marker genes')
    parser.add_argument('-n', action="store", dest='sampleName', default=None, help='sample name for the current mapping')


    # output and output options
    parser.add_argument('-o', action="store", dest='output', default=None, help='name of output file')
    parser.add_argument('-v', action='store', type=int, default=None, dest='verbose', help='Verbose levels')
    parser.add_argument('-y', action="store", dest='type_output', default=None, help='type of output that you want to print',choices=['base.coverage', 'insert.raw_counts', 'insert.scaled_counts'])


    # help
    parser.add_argument('--version', action='version', version='%(prog)s {0} on python {1}'.format(version_tool, sys.version.split()[0]))
    parser.add_argument('--test', action='store_true', default=None, dest='test_motu', help='test that motus has all the dependencies and is working correctly')

    # input for append
    parser.add_argument('-d', action="store", default=None, dest='directory_append', help='directory from where to take the files to append')

    # others
    parser.add_argument('-t', type=int, action="store", dest='threads', default=None, help='Number of threads to be used.')
    parser.add_argument('-I', action="store", default=None, dest='profile_bam_file', help='name of the bam file to save the intermediate bam file during profiling')

    # filters
    parser.add_argument('-min_perc_id', action="store", default=None, dest='min_perc_id', help='minimum percentage of identity when filtering - choose between 97 and 100')
    parser.add_argument('-min_clip_length', action="store", default=None, dest='min_clip_length', help='min. length of alignment when clipped')
    parser.add_argument('-min_perc_align', action="store", default=None, dest='min_perc_align', help='min. percent of the query that must be aligned, between 0 and 100')
    parser.add_argument('-l', type=int, action="store", dest='min_len_align_length', default=None, help='Minimum length of the alignment')

    args = parser.parse_args()

    # print menu for the commands

    # return args
    return args