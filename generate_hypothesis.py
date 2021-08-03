"""
Script for generating simple hypotheses given a domain file (see `examples/`).


How to use:
`$ python generate_hypothesis.py --domain_file=examples/temperature.json --n_hypotheses=100`

Contributors:

* Adelson de Araujo (a.dearaujo@utwente.nl)
"""


import json
import fire
import numpy as np

import hypothesis_parser as parser


def generate_actions(variables: list, modifiers: list,
                     interactors: list, qualifiers: list) -> list:
    """Generates a list of possible action structured with keys given input combination.
            Possible structures:
                1. Action = Variable + Qualifier + Modifier
                2. Action = Modifier + Variable + Qualifier
                3. Action = Variable + Qualifier + Interactor + Value
                4. Action = Variable + Qualifier + Interactor + Variable + Qualifier
                4. Action = Variable + Qualifier + Interactor + Qualifier
                    (assuming second qualifier refers to the first variable)
                5. Action = Action and Action
                    (recursion is allowed)
    """
    actions = []
    for vi in variables:
        for qi in qualifiers:
            for mi in modifiers:
                # actions type 1
                actions.append({'variable': vi, 'qualifier': qi, 'modifier': mi})
                # actions type 2
                actions.append({'modifier': mi, 'variable': vi, 'qualifier': qi})
            for ii in interactors:
                # actions type 3
                actions.append({'variable': vi, 'qualifier': qi, 'interactor': ii,
                                'value':np.random.randint(100)})
                while True:
                    qj = np.random.choice(qualifiers)
                    if qj != qi:
                        break
                # actions type 4
                actions.append({'variable': vi, 'qualifier': qi, 'interactor': ii,
                                'variable_': vi, 'qualifier_': qj})
                # actions type 4
                actions.append({'variable': vi, 'qualifier': qi, 'interactor': ii,
                                'qualifier_': qj})
    composed_actions = []
    for i in range(len(actions)):
        # sample two actions of different variables (including those generated in this loop)
        while True:
            ai, aj = np.random.choice(actions, 2, replace=False)
            if ai['variable'] != aj['variable']:
                break
        # add numerical label to subsequent keys to avoid overriding ai's keys
        c = np.sum([1 if 'and' in k else 0 for k in {**ai, **aj}]) + 1
        aj = {f'{k}{c}':aj[k] for k in aj}
        # actions type 5
        composed_actions.append({**ai, 'and':'and', **aj})
    actions += composed_actions
    return actions


def main(domain_file='examples/temperature.json',
         n_hypotheses=-1,
         output_file='output_hypothesis.txt'):

    with open(domain_file, 'r') as f:
        domain = json.load(f)

    actions = [parser.Action(a) for a in generate_actions(**domain)]

    hypotheses = []
    for acx in actions:
        for acy in actions:
            h = parser.Hypothesis(acx, acy)
            if h.label==0:
                hypotheses.append(h.forms['direct']['text'])

    if n_hypotheses > 0:
        hypotheses = np.random.choice(hypotheses,
                                      n_hypotheses, replace=False)


    with open(output_file, 'w+') as f:
        f.write('\n'.join(hypotheses))


if __name__=="__main__":
    fire.Fire(main)
