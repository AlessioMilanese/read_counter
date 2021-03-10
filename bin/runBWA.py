#!/usr/bin/env python

# ============================================================================ #
# runBWA.py: first step of the mOTU-LGs profiling
#
# ============================================================================ #

from __future__ import division
import os
import sys
import argparse
import shlex
import time
import subprocess
import re
import errno


# ------------------------------------------------------------------------------
# function to check if a specific tool exists
# ------------------------------------------------------------------------------
def is_tool(name):
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == errno.ENOENT:
            return False
    return True

# ------------------------------------------------------------------------------
# run bwa on a file that contains reads that are single end
# ------------------------------------------------------------------------------
def runBWA_singleEnd(strFilteredReadFile, reference, msamPercID, msamminLength, threads, msamOverlap,verbose):
    if verbose >= 6: sys.stderr.write("bwa: values. msamPercID: "+str(msamPercID)+" msamminLength: "+str(msamminLength)+" msamOverlap: "+str(msamOverlap)+"\n")
    try:
        from subprocess import DEVNULL
    except ImportError:
        DEVNULL = open(os.devnull, 'wb')

    if (threads):
        threadsFlag = " -t " + str(threads)
    else:
        threadsFlag = " -t 1"

    zippedInput = False
    # bwa can handle .gz files
    #if (strFilteredReadFile.endswith(".gz")):
    #    unzipCMD = "gunzip -c " + strFilteredReadFile
    #    zippedInput = True
    #    if not(is_tool("gunzip")):
    #        sys.stderr.write("[E::map_db] Error: gunzip is not installed. Cannot unzip the files\n")
    #        sys.exit(1)
    if (strFilteredReadFile.endswith(".bz2")):
        unzipCMD = "bunzip2 -c " + strFilteredReadFile
        zippedInput = True
        if not(is_tool("bunzip2")):
            sys.stderr.write("[E::map_db] Error: bunzip2 is not installed. Cannot unzip the files\n")
            sys.exit(1)

    # check that bwa is in the path
    if not(is_tool("bwa")):
        sys.stderr.write("[E::map_db] Error: BWA is not in the path. Cannot map the reads\n")
        sys.exit(1)


    # run bwa
    try:
        if (zippedInput):
            bwaCMD = "bwa mem -v 1 -a" +  threadsFlag + " " + reference + " -"
        else:
            bwaCMD = "bwa mem -v 1 -a" +  threadsFlag + " " + reference + " " + strFilteredReadFile

        if verbose >= 6: sys.stderr.write("bwa call:\n"+bwaCMD+"\n")

        if (zippedInput):
            unzip_popenCMD = shlex.split(unzipCMD)
            unzip_cmd = subprocess.Popen(unzip_popenCMD,stdout=subprocess.PIPE,)

            bwa_popenCMD = shlex.split(bwaCMD)
            bwa_cmd = subprocess.Popen(bwa_popenCMD,stdin=unzip_cmd.stdout,stdout=subprocess.PIPE,stderr=DEVNULL)
        else:
            bwa_popenCMD = shlex.split(bwaCMD)
            bwa_cmd = subprocess.Popen(bwa_popenCMD,stdout=subprocess.PIPE,stderr=DEVNULL)

        min_perc_id=msamPercID
        min_length_align=msamminLength
        min_perc_cover=msamOverlap

        if verbose >= 5: sys.stderr.write(" [map_db] Filter in bwa: MIN_PERC_ID:"+str(min_perc_id)+" MIN_LENGTH_ALIGN: "+str(min_length_align)+" MIN_PERC_COVER: "+str(min_perc_cover)+" \n")

        for line in bwa_cmd.stdout:
            #filter lines
            line = line.decode('ascii')
            if line[0]!="@": # header
                arr = line.split("\t")
                if not((arr[1] == '4') or (arr[2] == '*') or (arr[5] == '*')):
                    len_seq = 0

                    min_query_al = 0

                    tott = 0

                    flag2 = False
                    tot = 0
                    for n,i in (re.findall('(\d+)([IDMSHX=])', arr[5])):
                        tott = tott + int(n)
                        if i == 'M' or i == 'D' or i == 'X' or i == '=':
                            tot = tot + int(n)
                        if i != 'I' and i != 'S' and i!= 'H':
                            len_seq = len_seq + int(n)
                        if i != 'H' and i != 'S' and i!= 'D':
                            min_query_al = min_query_al + int(n)

                    if tot >= float(min_length_align):
                        flag2 = True

                    flag1 = False
                    if ((int(arr[11].split(":")[2])/float(len_seq)) < (1-float(min_perc_id))): # TODO: here we assume that the NM value is in position 11, it should be checked
                        flag1 = True

                    # min. percent of the query that must be aligned, between 0 and 100 (required)
                    flag3 = False
                    if (float(min_query_al)/float(tott)) >= (float(min_perc_cover)/100 ):
                        flag3 = True

                    if flag1 and flag2 and flag3:
                        yield line

        #check that bzip finished correctly
        if (zippedInput):
            unzip_cmd.stdout.close()
            return_code = unzip_cmd.wait()
            if return_code:
                sys.stderr.write("[E::map_db] Error. bunzip2 failed\n")
                sys.exit(1)


        # chack that bwa finished correctly
        bwa_cmd.stdout.close()
        return_code = bwa_cmd.wait()
        if return_code:
            sys.stderr.write("[E::map_db] Error. bwa failed\n")
            sys.exit(1)


    except:
        sys.stderr.write("[E::map_db] Error. Cannot call bwa on the file "+strFilteredReadFile+"\n")
        sys.exit(1)


# ------------------------------------------------------------------------------
# run the bwa mapping considering all files as single end
# ------------------------------------------------------------------------------
def runBWAmapping(forwardReads, reverseReads, singleReads, reference, threads, verbose, lane_id, msamminLength_from_motus):
    # parameters for msamtools are fixed
    msamPercID = 0.97
    msamminLength = msamminLength_from_motus
    msamOverlap = 45

    ## check that the files exists
    if (forwardReads):
        if not os.path.isfile(forwardReads):
            sys.stderr.write("[E::map_db] Error: "+forwardReads+': No such file.\n')
            sys.exit(1)
        if not os.path.isfile(reverseReads):
            sys.stderr.write("[E::map_db] Error: "+reverseReads+': No such file.\n')
            sys.exit(1)
    if (singleReads):
        if not os.path.isfile(singleReads):
            sys.stderr.write("[E::map_db] Error: "+singleReads+': No such file.\n')
            sys.exit(1)

    # files
    sam_lines = list()
    mapped_sam_lines = list()
    sam_header = list()

    # computation for and rev --------------------------------------------------
    if (forwardReads):
        if verbose>2: start_time = time.time()

        #forward -----
        output_fwd = runBWA_singleEnd(forwardReads, reference, msamPercID, msamminLength, threads, msamOverlap,verbose)
        for line_b in output_fwd:
            line = line_b#.decode('ascii') # convert from binary to str
            if (not line.startswith("@")):
                orientation = "."+lane_id+'/1'
                line = line.replace("\t", orientation+"\t", 1)
                mapped_sam_lines.append(line)
            else:
                sam_header.append(line)

        if verbose>2: sys.stderr.write(" [map_db](map forward reads) " + str("{0:.2f}".format(time.time() - start_time))+" sec\n")

        # reverse -----
        if verbose>2: start_time = time.time()

        output_rev = runBWA_singleEnd(reverseReads, reference, msamPercID, msamminLength, threads, msamOverlap,verbose)

        for line_b in output_rev:
            line = line_b#.decode('ascii') # convert from binary to str
            if (not line.startswith("@")):
                orientation = "."+lane_id+'/2'
                line = line.replace("\t", orientation+"\t", 1)
                mapped_sam_lines.append(line)

        if verbose>2: sys.stderr.write(" [map_db](map reverse reads) " + str("{0:.2f}".format(time.time() - start_time))+" sec\n")

        # sort for and rev
        if verbose>2: start_time = time.time()
        mapped_sam_lines.sort()
        if verbose>2: sys.stderr.write(" [map_db](sort reads) " + str("{0:.2f}".format(time.time() - start_time))+" sec\n")


    # computation single -------------------------------------------------------
    if (singleReads):
        if verbose>2: start_time = time.time()

        output_single = runBWA_singleEnd(singleReads, reference, msamPercID, msamminLength, threads, msamOverlap,verbose)
        for line_b in output_single:
            line = line_b#.decode('ascii') # convert from binary to str
            if (not line.startswith("@")):
                orientation = "."+lane_id+'.single'
                line = line.replace("\t", orientation+"\t", 1)
                mapped_sam_lines.append(line) #single ends are just appended (no need to sort)
            else:
                if (forwardReads==""): # if the header has not been printed already, then we print the header
                    sam_header.append(line)

        if verbose>2: sys.stderr.write(" [map_db](map single reads) " + str("{0:.2f}".format(time.time() - start_time))+" sec\n")

    return mapped_sam_lines
