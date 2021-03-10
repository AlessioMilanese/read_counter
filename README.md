`read_counter` is a tool to count the number of reads (from a fastq file) that map to a set of nucleotide sequences (in a fasta format).

# Table of contents

* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Quick usage](#quick-usage)
* [Advance usage](#advance-usage)
    * [Count reads](#count-reads)
    * [Index fasta](#index-fasta)
    * [Merge](#merge)


# Introduction

# Requirements

# Installation

# Quick usage

# Advance usage

### Count reads

### Index fasta

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
The reads that map to `geneA` and `geneC` are summed up and printed in the output under the id `cluster_2`.

### Merge
