N_SHARD=1
DEVICE_LIST=(1 2 3 4 5 6 7)
LOG_PATH="log"
for i in $(seq 0 $((N_SHARD-1))); do
    log_name="${LOG_PATH}/log_infer_lyrics_${i}.txt"
    len_cuda=${#DEVICE_LIST[@]}
    cur_device=${DEVICE_LIST[$((i%len_cuda))]}

    CUDA_VISIBLE_DEVICES=${cur_device} python -u infer.py \
        --n_shard ${N_SHARD} \
        --shard_rank ${i} > ${log_name} 2>&1 &
done