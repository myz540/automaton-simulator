import sys
import traceback


class Automaton:

    def __init__(self, states, final_states, alphabet):

        if isinstance(states, list) and len(states) > 0:
            self.states = states
        else:
            raise TypeError("States must be a list of strings with at least 1 element")

        if isinstance(final_states, list) and len(final_states) > 0:
            self.final_states = final_states
        else:
            raise TypeError("Final states must be a list of strings with at least 1 element")

        if isinstance(alphabet, list) and len(alphabet) > 0 \
                and all(isinstance(char, str) for char in alphabet) and all(len(char) == 1 for char in alphabet):
            self.alphabet = alphabet
        else:
            raise TypeError("Alphabet must be a non-empty list of string objects")


class DFA(Automaton):

    def __init__(self, states, final_states, alphabet):
        Automaton.__init__(self, states, final_states, alphabet)
        self.type = 'DFA'
        self.transitions = dict()
        self.current_state = self.states[0]
        self.input_string = None

    def add_transition(self, inputs, output):
        if isinstance(inputs, tuple) and len(inputs) == 2:
            start_state = inputs[0]
            input_char = inputs[1]

            if input_char not in self.alphabet:
                raise ValueError("Input character not in alphabet, invalid transition specified")

            if start_state not in self.states:
                raise ValueError("Input state not a valid state, invalid transition specified")

            if output not in self.states:
                raise ValueError("Output state not a valid state, invalid transition specified")

            if inputs in self.transitions.keys():
                raise KeyError("Transition function already specified for the given input state and input character,"
                               "the DFA can only have one output state for each input state/character")

            self.transitions[inputs] = output

        else:
            raise TypeError("Invalid input. Input must be a tuple of length 2, with the first element being the current"
                            "state, and the second element being the input character")

    def parse(self, string, max_tries=100):
        if isinstance(string, str):
            self.input_string = string
        else:
            raise ValueError("Input string must be of type 'str'")

        self.current_state = self.states[0]
        accepted = True
        current_try = 0

        for symbol in self.input_string:

            if current_try >= max_tries:
                print("String: ", self.input_string, " results in non-final state after ", max_tries, " transitions")
                print("The automaton is either in an infinite loop and the input string is not accepted, or "
                      "the max number of tries needs to be increased")
                accepted = False
                break

            if (self.current_state, symbol) not in self.transitions.keys():
                print("String: ", self.input_string, " is not accepted by the DFA")
                accepted = False
                break
            else:
                self.current_state = self.transitions[(self.current_state, symbol)]

            current_try += 1

        if accepted:
            if self.current_state not in self.final_states:
                print("String: ", self.input_string, " finished parsing but the automaton ended up in a non-final state,"
                                                     " the string is rejected")
                accepted = False
            else:
                print("String: ", self.input_string, " finished parsing and the automaton ended up in a final state,"
                                                     " the string is accepted")
        return accepted


class DPDA(Automaton):

    def __init__(self, states, final_states, alphabet):
        Automaton.__init__(self, states, final_states, alphabet)
        self.type = 'DPDA'
        self.transitions = dict()
        self.current_state = self.states[0]
        self.input_string = None
        self.stack = ['z']
        self.actions = ['push', 'pop', 'nothing']

    def add_transition(self, inputs, output):
        if isinstance(inputs, tuple) and len(inputs) == 3 and isinstance(output, tuple) and len(output) == 2:
            start_state = inputs[0]
            input_char = inputs[1]
            top = inputs[2]
            output_state = output[0]
            output_action = output[1]

            if input_char not in self.alphabet:
                raise ValueError("Input character not in alphabet, invalid transition specified")

            if start_state not in self.states:
                raise ValueError("Input state not a valid state, invalid transition specified")

            if top not in self.alphabet and top != 'z':
                raise ValueError("Top of stack must be in the alphabet or 'z'")

            if output_state not in self.states:
                raise ValueError("Output state not a valid state, invalid transition specified")

            if output_action not in self.actions:
                raise ValueError("Output action must be 'push', 'pop', or 'nothing'")

            if inputs in self.transitions.keys():
                raise KeyError("Transition function already specified for the given input state and input character,"
                               "the DPDA can only have one output state/action for each input state/character")

            self.transitions[inputs] = output

        else:
            raise TypeError("Invalid input or output. Input must be a tuple of length 2, with the first element being "
                            "the current state, and the second element being the input character. Output must be a "
                            "tuple of length 2 with the first element being the output state, and the second element"
                            "being the action to be taken on the stack")

    def _stack_action(self, action, symbol):
        if action == 'push':
            self.stack.append(symbol)
        elif action == 'pop':
            self.stack.pop()
        elif action == 'nothing':
            pass
        else:
            raise ValueError("Invalid stack action")

    def _top(self):
        return self.stack[-1] if len(self.stack) > 0 else None

    def parse(self, string, max_tries=100):
        if isinstance(string, str):
            self.input_string = string
        else:
            raise ValueError("Input string must be of type 'str'")

        self.current_state = self.states[0]
        self.stack = ['z']
        accepted = True
        current_try = 0

        for symbol in self.input_string:

            if current_try >= max_tries:
                print("String: ", self.input_string, " results in non-final state after ", max_tries, " transitions")
                print("The automaton is either in an infinite loop and the input string is not accepted, or "
                      "the max number of tries needs to be increased")
                accepted = False
                break

            if (self.current_state, symbol, self._top()) not in self.transitions.keys():
                print("String: ", self.input_string, " is not accepted by the DFA")
                accepted = False
                break
            else:
                output = self.transitions[(self.current_state, symbol, self._top())]
                self.current_state = output[0]
                self._stack_action(output[1], symbol)

            current_try += 1

        if accepted:
            if self._top() == 'z':
                self.current_state = self.final_states[0]

            if self.current_state not in self.final_states:
                print("String: ", self.input_string, " finished parsing but the automaton ended up in a non-final state,"
                                                     " the string is rejected")
                accepted = False
            else:
                print("String: ", self.input_string, " finished parsing and the automaton ended up in a final state,"
                                                     " the string is accepted")
        return accepted


def create_dfa_ex1():
    """
    Example DFA that accepts strings of the form abb{a,b}*
    :return: DFA
    """
    alphabet = ['a', 'b']
    states = ['q0', 'q1', 'q2', 'q3']
    final_states = ['q3']
    try:
        automaton = DFA(states, final_states, alphabet)

        automaton.add_transition(('q0', 'a'), 'q1')
        automaton.add_transition(('q1', 'b'), 'q2')
        automaton.add_transition(('q2', 'b'), 'q3')
        automaton.add_transition(('q3', 'a'), 'q3')
        automaton.add_transition(('q3', 'b'), 'q3')

        return automaton

    except Exception as e:
        print(sys.exc_info())
        print(traceback.format_exc())


def create_dpda_ex1():
    """
    Example DPDA that accepts strings of the form (a^n)(b^n) for n >= 1
    :return: DPDA
    """
    alphabet = ['a', 'b']
    states = ['q0', 'q1', 'q2', 'q3']
    final_states = ['q3']
    try:
        automaton = DPDA(states, final_states, alphabet)
        
        automaton.add_transition(('q0', 'a', 'z'), ('q1', 'push'))
        automaton.add_transition(('q1', 'a', 'a'), ('q1', 'push'))
        automaton.add_transition(('q1', 'b', 'a'), ('q2', 'pop'))
        automaton.add_transition(('q2', 'b', 'a'), ('q2', 'pop'))

        return automaton

    except Exception as e:
        print(sys.exc_info())
        print(traceback.format_exc())


if __name__ == "__main__":

    #dfa = create_dfa_ex1()
    #dfa.parse('ab')
    #dfa.parse('ba')
    #dfa.parse('abb')
    #dfa.parse('abbaabbaababa')
    #dfa.parse('abc')
    #dfa.parse('abbbbbbaaaaababababab')
    #dfa.parse('aa')

    dpda = create_dpda_ex1()
    dpda.parse('ab')
    dpda.parse('ba')
    dpda.parse('aaaabbbb')
    dpda.parse('aabbbb')
    dpda.parse('aaaabb')
    dpda.parse('aaaaaaaaabbbbbbbbb')