# Faithful and Controllable Dialogue Response Generation with Dataflow Transduction and Constrained Decoding

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img align="right" src="https://avatars2.githubusercontent.com/u/9585815?s=200&v=4" width="18%">

This repository contains code and instructions for reproducing the experiments in the paper
[The Whole Truth and Nothing But the Truth: Faithful and Controllable Dialogue Response Generation with Dataflow Transduction and Constrained Decoding](https://arxiv.org/abs/2209.07800) (Findings of ACL 2023). [[paper](https://aclanthology.org/2023.findings-acl.351/)] [[video](https://www.youtube.com/watch?v=m_yVepRYOyM&t=22s)]

![Approach Overview](./assets/dataflow2text.png?raw=true)

## Introduction (WIP)

There are two key components in our framework: **dataflow transduction** and **constrained decoding**,
implemented by the [dataflow2text](./dataflow2text) package and the [clamp](./clamp) package, respectively.

- These two packages currently use two different Python versions.
  The `dataflow2text` package relies on [the structural pattern matching feature introduced in Python 3.10](https://docs.python.org/3/whatsnew/3.10.html),
  whereas the `clamp` package heavily relies on [PyTorch](https://pytorch.org/) and [🤗 Transformers](https://huggingface.co/docs/transformers/index).
- The clamp package is a simplified version of the code for [Semantic Parsing with Constrained LM](https://github.com/microsoft/semantic_parsing_with_constrained_lm/).

To reproduce the SMCalFlow2Text results reported in the paper, please refer to the [worksheets](./worksheets/) folder.
You will need to create two python virtual environments.

```bash
conda env create --file=dataflow2text/environment.yml --name=dataflow2text_py310

conda env create --file=clamp/environment.yml --name=clamp_py37
```

More details coming soon!

## Citation

If you use any source code or data included in this repo, please cite our paper.

```bib
@article{SMCalflow2Text2023,
    title={The Whole Truth and Nothing But the Truth: Faithful and Controllable Dialogue Response Generation with Dataflow Transduction and Constrained Decoding}, 
    author={Hao Fang and 
      Anusha Balakrishnan and 
      Harsh Jhamtani and 
      John Bufe and 
      Jean Crawford and 
      Jayant Krishnamurthy and 
      Adam Pauls and 
      Jason Eisner and 
      Jacob Andreas and 
      Dan Klein},
    booktitle = {Findings of the Association for Computational Linguistics: ACL 2023},
    year={2023},
}
```
