#!/usr/bin/env bash
set -e

# NOTE: use the `dataflow2text_py310` environment.
python -c "import sys; assert(sys.version_info.major==3 and sys.version_info.minor==10)"

data_dir="../../data/smcalflow2text"

outdir="output/step02_process_data"
mkdir -p ${outdir}

python -m dataflow2text_domains.calflow.experiments.process_data_without_execution_results \
  --data_tsv "${data_dir}/valid.tsv" \
  --outbase ${outdir}/valid

python -m dataflow2text_domains.calflow.experiments.process_data_without_execution_results \
  --data_tsv "${data_dir}/train.tsv" \
  --outbase ${outdir}/train
