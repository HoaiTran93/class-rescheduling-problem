#!/bin/bash

file_name=$1

start_ms=$(ruby -e 'puts (Time.now.to_f * 1000).to_i')
python main.py ./data/test1
end_ms=$(ruby -e 'puts (Time.now.to_f * 1000).to_i')

result_ms=$((end_ms - start_ms))

echo -e $result_ms >> $file_name
