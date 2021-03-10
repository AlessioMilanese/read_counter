# index
./read_counter index -db test/test.fasta &> /dev/null
./read_counter map -db test/test.fasta -s test/test.fq -o test/RES_temp &> /dev/null

cmp --silent test/RES_temp test/correct_result.map && echo 'You have the same result as the test' || echo '### WARNING: Files Are Different! ###'

# remove file created
rm test/test.fasta.*
rm test/RES_temp
