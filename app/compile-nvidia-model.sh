#!/bin/bash -x

mkdir /sd2_compile_dir_512
touch /sd2_compile_dir_512/cudaplaceholder
tar -czvf /sd2_compile_dir_512_cuda.tar.gz /sd2_compile_dir_512/
aws s3 cp /sd2_compile_dir_512_cuda.tar.gz s3://sdinfer/sd2_compile_dir_512_cuda.tar.gz
aws s3api put-object-acl --bucket sdinfer --key sd2_compile_dir_512_cuda.tar.gz --acl public-read
