#### Mutated CRUXEval dataset:

- Mutated dataset: `{muator}_{num}.jsonl`
- New sampleID: `{mutator}\_sample\_from\_{oldID}\_to\_{newID}`



#### Mutators

- **For2While**

For loop to while loop.

```python
# For loop
def f(var1):
    var2 = len(var1)
    for var3 in range(2, var2):
       var1.sort()
    return var1

# While loop
def f1(var1):
    var2 = len(var1)
    idx = 2
    while idx < var2:
			var1.sort()
			idx += 1
    return var1
```

- **AugAssign2Assign**

```python
# AugAssign
x += 1
# Assign
x = x + 1
```

- **Deadcode_Assign2Ternary**

Each assignment operation has a probability `p` (0.5 currently) of being converted.

```python
x = y

x = y if 1>0 else z
```

- **Deadcode_Add_IndependentVar**

Random add random independent variable like (`var_9tl = 59`) at random (p = 0.5) location.

```python
x = 1
y = 2
z = 3

x = 1
y = 2
var_9tl = 59
z = 3
```

- **AssignUnfoldding**

Each assignment operation has a probability `p` (0.5 currently) of being converted.

```python
a = b + c

a = b; a = a + c
```

- **ConstantUnfoldding**

```python
a = 5
 
a = (7 -2)
```

### Testing Results
https://docs.google.com/spreadsheets/d/1yL7ayoBuShTkTuEwIWZKzHYcVFu5u5Rv7GNG-qxscdU/edit?gid=0#gid=0



### Python scripts

- `mutators.py`:  Mutator definitions.
- `Mutate.py`: Main function.
- `tmp.py`: Temp file for evaluate the function in dataset.
