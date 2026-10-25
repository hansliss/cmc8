"""Check the limits of pure transfers in the current single-port abstraction.

Run: python3 -m experiments.exchange_routes
This is a restricted reachability argument, not a proof about all ALU-based
algorithms or the actual CMC8. It explains why an EXR load/store recipe
needs a path/holding detail absent from our original model.
"""
from collections import deque


def transfer_states():
    """Reachable (R(A), X, BR) tokens through the four existing copy paths."""
    initial = ('a', 'b', 'old-buffer')
    paths = ((2, 0), (2, 1), (0, 2), (1, 2))
    pending = deque([initial])
    seen = {initial}
    while pending:
        state = pending.popleft()
        for destination, source in paths:
            result = list(state)
            result[destination] = state[source]
            result = tuple(result)
            if result not in seen:
                seen.add(result)
                pending.append(result)
    return seen


def xor_swap(value, x, *, same_register=False):
    """Mathematical three-XOR swap, including the self-alias counterexample."""
    if same_register and value != x:
        raise ValueError('One register cannot start with two different values')
    cells = [value] if same_register else [value, x]
    a_index, x_index = 0, 0 if same_register else 1
    cells[a_index] ^= cells[x_index]
    cells[x_index] ^= cells[a_index]
    cells[a_index] ^= cells[x_index]
    return cells[a_index], cells[x_index]


def main():
    states = transfer_states()
    reachable = any(state[:2] == ('b', 'a') for state in states)
    print(f'Pure-copy abstraction: {len(states)} reachable states; swap reachable={reachable}')
    print('This excludes ALU encodings, hidden latches and alternate register ports.')
    print('Three-XOR self-alias counterexample: EXR X with X=81 ->',
          tuple(f'{value:02X}' for value in xor_swap(0x81, 0x81, same_register=True)))
    print('Selected v014 H019 instead uses an explicit provisional ALU-input holding latch.')


if __name__ == '__main__':
    main()
