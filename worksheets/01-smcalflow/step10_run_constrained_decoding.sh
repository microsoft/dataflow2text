#!/usr/bin/env bash
set -e

# NOTE: use the `clamp_py37` environment.
python -c "import sys; assert(sys.version_info.major==3 and sys.version_info.minor==7)"

model_loc="models/codet5-base-finetuned-with-execution"
processed_data_dir="output/step02_process_data"
grammar_base_dir="output/step01_create_cfg_productions"

output_dir="output/step10_run_constrained_decoding"
mkdir -p ${output_dir}

python -m clamp_experiments.run_constrained_decoding \
  --model_loc ${model_loc} \
  --train_data_jsonl ${processed_data_dir}/train.jsonl \
  --eval_data_jsonl ${processed_data_dir}/valid.jsonl \
  --grammar_base_dir ${grammar_base_dir}/valid \
  --output_dir ${output_dir}/experiments \
  1> ${output_dir}/stdout \
  2> ${output_dir}/stderr
