#!/usr/bin/env bash
set -e

# NOTE: use the `clamp_py37` environment.
python -c "import sys; assert(sys.version_info.major==3 and sys.version_info.minor==7)"

experiments_base_dir="output/step10_run_constrained_decoding/experiments"

output_dir="output/step11_gather_decoding_results"
mkdir -p ${output_dir}

python -m clamp_experiments.gather_decoding_results \
  --experiments_base_dir ${experiments_base_dir} \
  --output_dir ${output_dir} \
  1> ${output_dir}/stdout \
  2> ${output_dir}/stderr
