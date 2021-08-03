"""
Script for evaluating simple hypotheses given a domain file (see `examples/`).


How to use:
`$ python hypothesis_parser.py --hypothesis="if temperature increases then brightness increases" --domain_file=examples/temperature.json`

Contributors:

* Adelson de Araujo (a.dearaujo@utwente.nl)
"""

import re
import json
import numpy as np
import pandas as pd
import autocorrect
import fire


def preprocess(text: str, language: str = 'en',
               rm_ponct: bool = True, clean_words: bool = True) -> str:
    """Applies word-level autocorrection and removes ponctuation."""
    if language:
        spell = autocorrect.Speller(language)
        text = spell(text)
    if rm_ponct:
        text = re.sub(r'[^\w\s]','', text)
    if clean_words:
        text = re.sub(r'[^a-zA-Z ]', '', text)
    return text


# Actions

class Action:
    """Wrapper to operate individual actions and their respective tokens."""

    def __init__(self, tokens: dict):
        self.tokens = tokens
        self.text = self.__repr__()
        self.syntax = ' '.join([preprocess(t, language=False) for t in self.tokens])

    def __repr__(self):
        return ' '.join([str(self.tokens[t]) for t in self.tokens])

    def get_by(self, key: str) -> list:
        return [self.tokens[t] for t in self.tokens if key in t]

    def compare_the_same_variable(self) -> bool:
        return self.tokens.get('variable') == self.tokens.get('variable_') \
                 and self.tokens.get('qualifier') != self.tokens.get('qualifier_')

    def is_composed(self) -> bool:
        return 'and' in self.tokens

    def something_changing(self) -> bool:
        return (self.get_by('interactor') + self.get_by('modifier') != ['remains the same']) \
            and len(self.get_by('interactor')+self.get_by('modifier')) > 0

    def variables_have_conditions(self) -> bool:
        return len(self.get_by('qualifier')) >= len(self.get_by('variable'))

    def has_variable_on(self, action_y) -> bool:
        x = [f"{i} {j}" for i, j  in zip(self.get_by('variable'),self.get_by('qualifier'))]
        y = [f"{i} {j}" for i, j  in zip(action_y.get_by('variable'),action_y.get_by('qualifier'))]
        for i in x:
            for j in y:
                if i == j:
                    return True
        return False


def a_tokenize(action: str, variables: list, modifiers: list,
               interactors: list, qualifiers: list) -> dict:
    tokens = {}
    if len(action) == 0:
        return tokens
    t = []
    [[t.append((_.start(), v, 'variable')) for _ in re.finditer(v, action)] for v in variables]
    [[t.append((_.start(), m, 'modifier')) for _ in re.finditer(m, action)] for m in modifiers]
    [[t.append((_.start(), i, 'interactor')) for _ in re.finditer(i, action)] for i in interactors]
    [[t.append((_.start(), q, 'qualifier')) for _ in re.finditer(q, action)] for q in qualifiers]
    [t.append((_.start(), 'and', 'and')) for _ in re.finditer('and', action)]
    t.sort(key=lambda tup: tup[0])
    flag = True
    c, c_ = list(range(1,1+len(list(re.finditer(' and ', action))))), ''
    for n, i in enumerate(t):
        if i[2] not in tokens.keys() and flag:
            tokens[i[2]] = i[1]
            if ' and ' in action and i[0] > action.find(' and '):
                flag = False
        elif 'and' in tokens.keys():
            if i[0] < action.find(' and '):
                tokens[i[2]+'_'] = i[1]
            else:
                if len(c)==0:
                    c_ = c_+'_'
                else:
                    c_ = str(c.pop())
                tokens[i[2]+c_] = i[1]
        else:
            tokens[i[2]+'_'] = i[1]
    return tokens



# Hypotheses

class Hypothesis:
    """ Parse hypothesis given (1) two Action objects, or given (2) a string.
    Attributes include `forms` (list), in which a single hypothesis representation
    is break down into other formats (e.g. if X then Y = Y if X) in calling
    Hypothesis.forms['texts'], with also the respective Hypothesis.forms['label']
    assigned during parsing.

    Labels:
        0 -> Appropriate hypothesis.
        1 -> Not enough variables, a hypothesis should always have at least two variables.
        2 -> You can only test an hypothesis if something changes.
        3 -> You did not described in which conditions your hypothesis applies.
        4 -> You are changing other variables at the same time, and you can't be sure which one has an effect.
        5 -> You are observing the same variables that you choose to change.
    """
    def __init__(self, action_x: Action, action_y: Action,
                from_text: str = '', variables: list = None, modifiers: list = None,
                interactors: list = None, qualifiers: list = None,
                debug: bool = False):
        if from_text:
            assert variables is not None and modifiers is not None and \
                    interactors is not None and qualifiers is not None, \
                "To parse an hypothesis from text, `variables`, `modifiers` + `interactors` " + \
                "and qualifiers are needed."
            act = h_tokenize(from_text)
            action_x = Action(a_tokenize(act['x'], variables, modifiers, interactors, qualifiers))
            action_y = Action(a_tokenize(act['y'], variables, modifiers, interactors, qualifiers))
        if debug:
            print(f"\nx: {action_x.text}\n >{action_x.tokens}" \
                  f"\ny: {action_y.text}\n >{action_y.tokens}")
        if action_x.text == action_y.text or len(action_x.text) == 0 or len(action_y.text)==0:
            self.label = 1
            self.forms = [
                {'text': f"if {action_x.text}", 'syntax': f"if {action_x.syntax}"},
                {'text': f"then {action_x.text}", 'syntax': f"then {action_x.syntax}"},
                {'text': f"{action_x.text}", 'syntax': f"{action_x.syntax}"}]
        else:
            if not action_x.something_changing() or not action_y.something_changing():
                self.label = 2
            elif not action_x.variables_have_conditions() or not action_y.variables_have_conditions():
                self.label = 3
            elif action_x.is_composed():
                self.label = 4
            elif action_x.has_variable_on(action_y):
                self.label = 5
            else:
                self.label = 0
            self.forms = {
                'direct': {"text":f"if {action_x.text} then {action_y.text}",
                     "syntax": f"if {action_x.syntax} then {action_y.syntax}"},
                'inverse': {"text":f"{action_y.text} if {action_x.text}",
                     "syntax": f"{action_y.syntax} if {action_x.syntax}"}
            }




def h_tokenize(hypothesis: str) -> dict:
    tokens = {}
    hypothesis = preprocess(hypothesis)
    if 'if ' == hypothesis[:3]:
        if ' then ' in hypothesis:
            tokens['x'], tokens['y'] = hypothesis[3:].split(' then ')
        else:
            tokens['x'], tokens['y'] = hypothesis[3:], ''
    elif ' if ' in hypothesis:
        tokens['x'], tokens['y'] = hypothesis.split(' if ')[::-1]
    elif 'then ' == hypothesis[:5]:
        tokens['x'], tokens['y'] = '', hypothesis[5:]
    else:
        tokens['x'], tokens['y'] = hypothesis, ''
    return tokens



def evaluate(hypothesis: str, domain_file: str, debug: bool = False) -> int:
    message = {
        0: "Appropriate hypothesis.",
        1: "Not enough variables, a hypothesis should always have at least two variables.",
        2: "You can only test an hypothesis if something changes.",
        3: "You did not described in which conditions your hypothesis applies.",
        4: "You are changing other variables at the same time, and you can't be sure which one has an effect.",
        5: "You are observing the same variables that you choose to change."
    }
    with open(domain_file) as f:
        domain = json.load(f)
    assert set(["variables", "modifiers", "interactors", "qualifiers"]) \
            == set(domain), \
        "Domain file is not correctly set, please include only `variables`," + \
        " `modifiers`, `interactors` and `qualifiers`."
    label = Hypothesis(None, None, hypothesis, debug=debug, **domain).label
    return label, message[label]



if __name__=="__main__":
    fire.Fire(evaluate)

    # # Test:
    # variables = ['temperature', 'radiation', 'brightness', 'light', 'heat']
    # modifiers = ['increases', 'decreases', 'remains the same']
    # interactors = ['is greater than', 'is smaller than', 'is equal to']
    # qualifiers = ['in point A', 'in point B', 'of the object']
    #
    # actions = [Action(a) for a in generate_actions(variables, modifiers, interactors, qualifiers)]
    # acx, acy = actions[-2:]
    # print(acx, a_tokenize(acx, variables, modifiers, interactors, qualifiers))
    #
    # h = []
    # for acx in actions:
    #     for acy in actions:
    #         h.append(Hypothesis(acx, acy))
    # print(h, h_tokenize(h[0].forms[0]['text']))
    #
    # h_l = []
    # for i in h:
    #     h_l += i.forms
    # h_l = pd.DataFrame(h_l)
    # h_l['label'].value_counts()
    #
    # # Debugging tokenization: Verifying hypothesis that were not parsed correctly
    # h_l['h2'] = h_l.apply(lambda x: Hypothesis(None, None, x['text'],
    #                                            variables, modifiers, interactors, qualifiers),
    #                       axis=1)
    # h_l['label2'] = h_l['h2'].apply(lambda x: x.forms[0]['label'])
    # print(h_l.loc[h_l['label']!=h_l['label2']].head())
