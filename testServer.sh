curlCmd="curl localhost:10000"
max=13
for i in `seq 1 $max`
do
eval $curlCmd
done
