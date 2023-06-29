#!/usr/bin/env bash
set -e

# NOTE: use the `clamp_py37` environment.
python -c "import sys; assert(sys.version_info.major==3 and sys.version_info.minor==7)"

data_dir="../../data/smcalflow2text"
predictions_json="output/step11_gather_decoding_results/predictions.json"

output_dir="output/step12_compute_evaluation_results"
mkdir -p ${output_dir}

python -m clamp_experiments.compute_evaluation_results \
  --data_tsv ${data_dir}/valid.tsv \
  --predictions_json ${predictions_json} \
  --output_dir ${output_dir} \
  1> ${output_dir}/stdout \
  2> ${output_dir}/stderr
