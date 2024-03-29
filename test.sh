# index
echo "RUN INDEX -----------------------------------------------------------"
./read_counter index -db test/test.fasta

echo "RUN MAP -------------------------------------------------------------"
./read_counter map -db test/test.fasta -s test/test.fq -o test/RES_temp

echo "RESULT --------------------------------------------------------------"
cmp --silent test/RES_temp test/correct_result.map && echo 'You have the same result as the test' || echo '### WARNING: Files Are Different! ###'

# remove file created
rm test/test.fasta.*
rm test/RES_temp
