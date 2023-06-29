#!/usr/bin/env bash
set -e

# NOTE: use the `dataflow2text_py310` environment.
python -c "import sys; assert(sys.version_info.major==3 and sys.version_info.minor==10)"

data_dir="../../data/smcalflow2text"

outdir="output/step01_create_cfg_productions"
mkdir -p ${outdir}

python -m dataflow2text_domains.calflow.experiments.create_cfg_productions \
  --data_tsv "${data_dir}/valid.tsv" \
  --preambles_and_metas_dir "${data_dir}" \
  --outdir ${outdir}/valid

python -m dataflow2text_domains.calflow.experiments.create_cfg_productions \
  --data_tsv "${data_dir}/train.tsv" \
  --preambles_and_metas_dir "${data_dir}" \
  --outdir ${outdir}/train
