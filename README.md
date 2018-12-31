# fusible-HST


## Requirement

- matplotlib (>=2.2.3)


## Usage

Run animation on a mass sequence:

```python
>>> from main import animate_mass_sequence

>>> seq = [[1, 0, 0, 0, 1],       # List of List
...        [0, 1, 0, 1, 0],
...        [0, 0, 2, 0, 0],
...        [0, 1, 0, 1, 0],
...        [1, 0, 0, 0, 1]]

>>> animate_mass_sequence(seq, mass_func_display_scale=1)
```
For more details, see the docstring of 
[animate_mass_sequence](https://github.com/seanhung21/fusible-HST/blob/master/main.py#L239)
and the [example code](https://github.com/seanhung21/fusible-HST/blob/master/example.py).
