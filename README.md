# hypothesis-parser

This repository has two basic functions. First, it can generate artificial
hypotheses given a domain file, and second, estimate its quality
following the advice provided in (Kroeze et al., 2018). This domain file
should be defined in the format of a grammar, with a defined set of elements.

To see how the grammar/domain file looks like, take a look in the `examples/`
folder.



## Instructions / How to use?


There are not installation setup for these scripts as a pip module. Instead,
you need to install some requirements, and run the scripts with the command
line interface, as described below.

```
$ pip install - r requirements.txt
```

To generate hypothesis and save them into a file:

```
$ python generate_hypothesis.py \
  --domain_file=examples/temperature.json \
  --n_hypotheses=100 \
  --output_file=hypothesis_out.txt
```

To evaluate a hypothesis with the command line interface:

```
$ python hypothesis_parser.py \
  --hypothesis="if temperature increases then brightness increases" \
  --domain_file=examples/temperature.json`
```
