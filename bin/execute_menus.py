import sys
import os
import shutil
import tempfile

# position of the script -------------------------------------------------------
path_this = os.path.realpath(__file__)
path_array = path_this.split("/")
relative_path = "/".join(path_array[0:-1])

# add /bin to the path ---------------------------------------------------------
try:
    if os.path.isdir(relative_path):
        sys.path.insert(0, relative_path)
    else:
        sys.stderr.write("[E::main] Error: "+relative_path+" directory is missing.\n")
        sys.exit(1)
except:
    sys.stderr.write("[E::main] Error: "+relative_path+" directory is missing.\n")
    sys.exit(1)

try:
    import count_reads as count_reads
except:
    sys.stderr.write("[E::main] Error: fail to load the script: "+relative_path+"/count_reads.py\n")
    sys.exit(1)

try:
    import runBWA as runbwa
except ImportError:
    sys.stderr.write("[E::main] Error: fail to load the script: "+relative_path+"/runBWA.py\n")
    sys.exit(1)

try:
    import index as index2
except ImportError:
    sys.stderr.write("[E::main] Error: fail to load the script: "+relative_path+"/index.py\n")
    sys.exit(1)

try:
    import utilities
except:
    sys.stderr.write("[E::main] Error: fail to load the script: "+relative_path+"/utilities.py\n")
    sys.exit(1)

#################################  COMMANDS  ###################################


################################################################################
# MAP command ------------------------------------------------------------------
def map(args):
    reference = "/Users/milanese/Desktop/read_couter_DB/test.fasta"
    # if there are different lanes, we need to split them
    singles = list()
    forw = list()
    reve = list()
    if (args.singleReads is not None): singles = args.singleReads.split(",")
    if (args.forwardReads is not None): forw = args.forwardReads.split(",")
    if (args.reverseReads is not None): reve = args.reverseReads.split(",")

    number_of_lanes = max(len(singles),len(forw),len(reve))
    if args.verbose > 2: sys.stderr.write("[main] Number of detected lanes: "+str(number_of_lanes)+"\n")

    # ----check input: check number of files for forw and rev ------------------
    if (args.forwardReads is not None):
        if len(forw) != len(reve):
            sys.stderr.write("[E::map_db] Error: number of files for forward reads ("+str(len(forw))+") is different from number of files for reverse reads ("+str(len(reve))+")\n")
            sys.exit(1)
    # set up before starting
    all_sam_lines = list()
    avg_length_reads = list()

    if args.verbose > 4:
        list_files_check = list()
        if (args.reverseReads is not None):
            list_files_check = list_files_check + forw
        if (args.singleReads is not None):
            list_files_check = list_files_check + singles
        utilities.print_n_reads(list_files_check,args.verbose)

    # we go through all the lanes
    for i in range(number_of_lanes):
        if args.verbose>2: sys.stderr.write("[main] Run bwa on lane "+str(i+1)+"\n")

        forward_reads = ""
        reverse_reads = ""
        single_reads = ""
        if (args.reverseReads is not None):
            if len(forw)> i:
                forward_reads = forw[i]
                reverse_reads = reve[i]
        if (args.singleReads is not None):
            if len(singles)> i:
                single_reads = singles[i]

        lane_id = "lane"+str(i)


        # check that the files are fastq and get the average reads length
        if forward_reads != "":
            avg_length_reads.append(utilities.is_fastq(forward_reads,args.verbose))
        if reverse_reads != "":
            avg_length_reads.append(utilities.is_fastq(reverse_reads,args.verbose))
        if single_reads != "":
            avg_length_reads.append(utilities.is_fastq(single_reads,args.verbose))


        sam_lines_list = runbwa.runBWAmapping( forward_reads, reverse_reads, single_reads, reference, args.threads, args.verbose, lane_id, args.min_len_align_length)

        all_sam_lines = all_sam_lines + sam_lines_list

        # calculate average length of the reads
        reads_avg_length = int(sum(avg_length_reads) / float(len(avg_length_reads)))


#-------# map genes ------------------------------------------------------------
    # prepare inputs
    file_data_coords = reference + ".coords"
    sample_name = "trial"
    if (args.sampleName is not None): sample_name = args.sampleName
    multThreshold = 3
    winnerThreshold = 0.95
    loserThreshold = 0.01

    output = ""

    # choose the proper value for min_len_align -------------------
    min_len_align = args.min_len_align_length
    if reads_avg_length != "unknown":
        if reads_avg_length < min_len_align:
            if args.verbose>1: sys.stderr.write("[W::main] Warning. Average read length ("+str(reads_avg_length)+") is lower than the -l filter ("+str(min_len_align)+"). We suggest to decrease the value of -l\n")

    if args.verbose>2: sys.stderr.write("[main] Minimum alignment length: "+str(min_len_align)+" (average read length: "+str(reads_avg_length)+")\n")

    # set min clipped length
    if args.verbose>4: sys.stderr.write("[main] Selecting the clipped length:...")
    #minClippedAlignLength = max(args.min_clip_length,min_len_align)
    minClippedAlignLength = min_len_align
    if args.verbose>4: sys.stderr.write(str(minClippedAlignLength)+"\n")



    # we have to filter the sam lines if they are not given as input -- note that the filtering (inside the second script) is done only for the one that are loaded, and not during bwa
    #all_sam_lines_input_count_reads = filter_sam.run_all_lines((args.min_perc_id/100),min_len_align,args.min_perc_align,all_sam_lines)
    all_sam_lines_input_count_reads = all_sam_lines


    read_counts = count_reads.count_reads(file_data_coords, sample_name, multThreshold, winnerThreshold, loserThreshold, minClippedAlignLength, output, args.type_output,args.verbose,all_sam_lines_input_count_reads, args.min_perc_id,min_len_align,args.min_perc_align)


    #save the mOTU read count, actually the mgc table
    if args.output is not None:
        try:
            mgc_temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
            os.chmod(mgc_temp_file.name, 0o644)
            mgc_temp_file.write(sample_name+"\n")
            for m, value in sorted(read_counts.items()):
                mgc_temp_file.write("{0}\t{1:.10f}\n".format(m, value))
        except:
            sys.stderr.write("[W::main] Warning: failed to save the intermediate mgc table\n")


        try:
            mgc_temp_file.flush()
            os.fsync(mgc_temp_file.fileno())
            mgc_temp_file.close()
        except:
            sys.stderr.write("[W::main] Warning: failed to save the intermediate mgc table\n")
        try:
            #os.rename(mgc_temp_file.name,args.output) # atomic operation
            shutil.move(mgc_temp_file.name,args.output) #It is not atomic if the files are on different filsystems.
        except:
            sys.stderr.write("[W::main] Warning: failed to save the intermediate mgc table\n")
            sys.stderr.write("[W::main] you can find the file here:\n"+mgc_temp_file.name+"\n")
    else:
        # we print to stdout
        print(sample_name)
        for m, value in sorted(read_counts.items()):
            print("{0}\t{1:.10f}".format(m, value))

    sys.exit(0)





################################################################################
# INDEX command ----------------------------------------------------------------
def index(args):
    index2.index(args.db,args.verbose)
    sys.exit(0)




################################################################################
# MERGE command ----------------------------------------------------------------
def merge(file_list):
    # we sort the files to have always the same order
    file_list.sort()

    headers = list()
    values = dict()
    for f in file_list:
        # first we set all to zeros
        for u in values:
            values[u].append(0)
        # now we check if adding new or replacing the zero we just added
        o = open(f,"r")
        headers.append(o.readline())
        for line in o:
            vals = line.rstrip().split("\t")
            if not vals[0] in values:
                values[u] = [0]*len(headers)
            values[u][-1] = vals[1]
        o.close()
    # print result
    print("\t".join(headers))
    # find order for the values
    clusters = values.keys()
    clusters.sort()
    for c in clusters:
        print("\t".join([c]+clusters[c]))
    sys.exit(0)
