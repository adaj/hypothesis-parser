import numpy as np


# Actions

def generate_actions(variables, modifers, interactors, qualifiers):
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


class Action:
    """Wrapper to operate with individual actions"""
    
    def __init__(self, a):
        self.a = a
        self.text = self.__repr__()
        
    def __repr__(self):
        return ' '.join([str(self.a[t]) for t in self.a])
        
    def remove_variable(self):
        """Randomly removes one of the variables in the action, so it is incomplete."""
        v_ = np.random.choice([k for k in self.a if 'variable' in k and 'variable_' not in k])
        _a = self.a.copy()
        _a.pop(v_, None)
        return _a
    
    def remove_modifier(self):
        """Removing the modifier of an action, so nothing is changing."""
        assert 'modifier' in self.a, \
            "Not possible, there is not modifiers on this action."
        _a = self.a.copy()
        _a.pop('modifier', None)
        return _a
    
    def change_second_variable(self, variables):
        """Changing the second variable to a different, thus comparing two incomparable variables."""
        assert 'variable_' in self.a, \
            "Not possible, there is not another variable to change."
        while True:
            vj = np.random.choice(variables)
            if self.a['variable'] != vj:
                break
        _a = self.a.copy()
        _a['variable_'] = vj
        return _a
            
    def remove_qualifier(self):
        """Removing the qualifier of an action, so it is incomplete."""
        assert 'qualifier' in self.a, \
            "Not possible, there is not qualifiers on this action."
        _a = self.a.copy()
        _a.pop('qualifier', None)
        return _a
        
    
    def change_second_variable(self, variables):
        """Changing the second variable to a different, thus comparing two incomparable variables."""
        assert 'variable_' in self.a, \
            "Not possible, there is not another variable to change."
        while True:
            vj = np.random.choice(variables)
            if self.a['variable'] != vj:
                break
        _a = self.a.copy()
        _a['variable_'] = vj
        return _a
            
    def remove_qualifier(self):
        """Removing the qualifier of an action, so it is incomplete."""
        assert 'qualifier' in self.a, \
            "Not possible, there is not qualifiers on this action."
        _a = self.a.copy()
        _a.pop('qualifier', None)
        return _a

    
# Hypotheses
    
def generate_valid_hypotheses(actions):
    """Generates a list of Action which hypothesis follow the grammar in Kroeze et al., 2019.
        For example, to test the effect of x in y, x should contain one variable and a modifier."""
    h = []
    for ax in actions:
        for ay in actions:
            if ax.text != ay.text:
                ax_one_var = np.sum([1 if 'variable' in a else 0 for a in ax.a]) == 1
                ax_one_qlf = np.sum([1 if 'interactor' in a else 0 for a in ax.a]) == 1
                if (ax_one_var or ax_one_qlf) and ax.a['variable'] not in ay.text:
                    h.append(f'if {ax} then {ay}')
                    h.append(f'{ay} if {ax}')
                    if ay.a['variable'][:5] == ax.text[:5]:
                        h.append(f'if {ax}, the {ay}')
    return h

def generate_error1_hypotheses(actions):
    """Invalid hypothesis according to criteria 1 (Kroeze et al., 2019).
        Hypothesis does not contain two variable names."""
    h = []
    return h

def generate_error2_hypotheses(actions):
    """Invalid hypothesis according to criteria 1 (Kroeze et al., 2019).
        Hypothesis does not contain a modifier in action x."""
    h = []
    return h
    
def generate_error3_hypotheses(actions):
    """Invalid hypothesis according to criteria 1 (Kroeze et al., 2019).
        Hypothesis is not syntactically correct."""
    h = []
    return h    
    
def generate_error4_hypotheses(actions):
    """Invalid hypothesis according to criteria 1 (Kroeze et al., 2019).
        Hypothesis manipulates more than one variable in action x."""
    h = []
    return h  

def generate_error5_hypotheses(actions):
    """Invalid hypothesis according to criteria 1 (Kroeze et al., 2019).
        Hypothesis which variables does not contain a qualifier."""
    h = []
    return h  

