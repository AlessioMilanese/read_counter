def index(fasta_file, verbose):
    # we first need to run bwa index

    # and second, create the .coord file
    w = open(fasta_file+".coord","w")
    gene_id = None
    fasta_seq = None
    with open(fasta_file, 'r') as f_h:
        for f in f_h:
            if f.startswith(">"):
                if gene_id is not None:
                    # we print the info of the previous gene
                    len_gene = str(len(fasta_seq))
                    w.write(gene_id+"\t"+len_gene+"\t1\t"+len_gene+"\t"+gene_id+"\n")
                gene_id = f.rstrip()[1:]
                fasta_seq = ""
            else:
                fasta_seq = fasta_seq + f.rstrip()

    # we print the info of the last gene
    len_gene = str(len(fasta_seq))
    w.write(gene_id+"\t"+len_gene+"\t1\t"+len_gene+"\t"+gene_id+"\n")

    w.close()
