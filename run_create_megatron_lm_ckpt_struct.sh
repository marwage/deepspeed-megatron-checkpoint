#!/bin/bash

set -e

export PYTHONPATH="$HOME/elasticity/repo/Megatron-LM"

python create_megatron_lm_ckpt_struct.py
