Tool to count reads that map to a set of sequences.


The command `read_counter index` does two things:
- First, it will first run `bwa index` internally on the input fasta file,
- Second, it will create a file `<fasta_id>.coords`.

This second file can be modified if you want to add padding or want to group the count of some genes.

`<fasta_id>.coords` is a tab delimited file with no header, and five columns:
1. gene_id (same as in the fasta file, but without the `>`)
2. gene length
3. position of starting of the gene sequence (i.e. where the left padding ends)
4. position of where the gene ends (i.e. where the right padding starts)
5. gene clusters

Regarding the second column, we count the number of bases in the gene.
Example, in black there is the gene sequence (start codon: ATG and stop codon: TAA), and in grey there is the padding.

The gene length is 12.
