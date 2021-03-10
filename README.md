`read_counter` is a tool to count the number of reads (from a fastq file) that map to a set of nucleotide sequences (in a fasta format).

# Table of contents

* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Quick usage](#quick-usage)
* [Advance usage: Index fasta](#advance-usage-index-fasta)
* [Advance usage: Count reads](#advance-usage-count-reads)
* [Advance usage: Merge](#advance-usage-merge)



# Introduction

Count reads that map to a set of genes is not always easy. If the genes are similar to each other, there will be reads that map to multiple genes with the same quality. Moreover, even if reads map to a gene, we would like to be able to filter only the high quality reads.

When working with gene catalog, we also have many genes that map to the same cluster. When counting the reads in this case, we would like to use the clusters as a unit count and not the single genes.

If you need to map reads from a metagenomic sample to a set of genes, you can use `read_counter`.




# Requirements

To run `read_counter` you will need:
The mOTU profiler requires:
* Python 3 (or higher)
* the Burrow-Wheeler Aligner v0.7.15 or higher ([bwa](https://github.com/lh3/bwa))



# Installation

```bash
git clone https://github.com/AlessioMilanese/read_counter.git
cd read_counter
export PATH=`pwd`:$PATH
```

You can test the installation with:
```
./test.sh
```
If the tool is working correctly, the last two lines will be:
```
RESULT --------------------------------------------------------------
You have the same result as the test
```

# Quick usage

For your analysis you will have (at least) two files:
- a fasta file with the sequence of the genes (database)
- a set of reads in a fastq format (query)

The first thing you have to do is to index the fasta file with the genes:
```
read_counter index -db test/test.fasta
```

where `test/test.fasta` is the file with the genes.

Second, you need to map the fastq file(s) to the genes. In case you have only one fastq file, you can call:
```
read_counter map -db test/test.fasta -s test/test.fq
```
Where `test/test.fq` is the fastq file with the reads.

In case you have paired end reads, and hence two files, you can run:
```
read_counter map -db test/test.fasta -f test_1.fq -r test_2.fq
```

The result is printed on the screen (standard output), but you can save it to a file with the `-o` option.

Finally, you might want to merge many profiles with the `merge` command:
```
read_counter map -db test/test.fasta -s test1.fq -o test1.map
read_counter map -db test/test.fasta -s test2.fq -o test2.map
read_counter merge test1.map test2.map
```






# Advance usage: Index fasta

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

![example_gene:AGGCATTTTT ATGCGGCAATAA GCGGGCGG](https://github.com/AlessioMilanese/read_counter/blob/master/pics/example_gene.png)

- The gene length (column 2) is 12.
- The position where the gene starts (column 3) is 11, which corresponds to the `A` in `ATG` (if you start to count from 1).
- The position where the gene ends (column 4) is 22, which corresponds to the `A` in `TAA` (if you start to count from 1).

Regarding the last column, it's helpful to specify genes that belong to the same cluster and should be counted together. Example of a `<fasta_id>.coords`:
```
geneA  1494  101  1594  cluster_1
geneB   984  101  1084  cluster_2
geneC  1737  101  1837  cluster_1
geneD  1431  101  1531  cluster_3
```
The reads that map to `geneA` and `geneC` are summed up and printed in the output under the id `cluster_1`.

Note that by default, `read_counter index` will consider the genes to have no padding (i.e. column 3 is `1` and column 4 is equal to the length of the genes). Additionally, the fifth column (with the clusters) will be set equal to the gene ids. If you wish to change the padding or the clustering, you will need to manually change the `<fasta_id>.coords` file.






# Advance usage: Count reads

The main function of this tool is to count reads, which you can do using the command `map`.
You will need to provide the fasta file (indexed before with `read_counter index`) with the `-db` option, as well as the fastq file(s).

You can provide a single file with:
```
read_counter map -db test/test.fasta -s test/test.fq
```

Or, paired end reads:
```
read_counter map -db test/test.fasta -f test_forward.fq -r test_reverse.fq
```

Or both:
```
read_counter map -db test/test.fasta -f test_forward.fq -r test_reverse.fq -s single.fq
```

Additionally, you can analyse samples that have been sequenced across multiple lanes:
```
read_counter map -db test/test.fasta -f test_lane1_FW.fq,test_lane2_FW.fq -r test_lane1_RV.fq,test_lane2_RV.fq
```

If you want to merge multiple profiles, you will need to specify the name of the samples when running the `map` command. Example:
```
read_counter map -db test/test.fasta -s sample_34_1.fq -n sample_34_1
```

This will be the header of the produced read count file:
```
sample_34_1
gene1   23.43782
gene2   0.374823
gene3   52.34783
```

As we said before, you can save the result to a file using the `-o` option:
```
read_counter map -db test/test.fasta -s sample_34_1.fq -o sample_34_1.map
```

You can filter for only reads that map with a certain number of nucleotide using the `-l` option. Example `-l 100` will select only reads that map with 100 nucleotides to a gene. Note that here it refers only to the gene sequence and not the padded region.

Finally, you can decide what to count with the `-y` command:
- `base.coverage` to evaluate the average coverage per base in the gene;
- `insert.raw_counts` to count the number of reads that map to a gene;
- `insert.scaled_counts` to count the number of reads that map to a gene and normalise it by the length of the gene. 






# Advance usage: Merge

The `merge` command doesn't have any option. When you call `read_counter merge`, all the files that follow are appended together. For example:
```
read_counter merge test1.map test2.map
```
will put together the two files `test1.map` and `test2.map`. Note that if your terminal supports it, you can use wildcards:
```
read_counter merge test*.map
```
will merge all files with the pattern `test*.map`, example: `test1.map`, `test2.map`, `test_number45.map`, `testA.map`, etc.
