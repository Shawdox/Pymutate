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

- **Assign2Ternary**

Each assignment operation has a probability `p` (0.5 currently) of being converted.

```python
x = y

x = y if 1>0 else z
```

- **Add_IndependentVar**

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

- **IfReverse**

```python
def f(): 
    a = 1
    b = 0
    if a:
        print("123")
    elif b:
        print("456")
    else:
        print("789")
    
    if not a:
        None
        
def mutated_f(): 
    a = 1
    b = 0
    if not a: 
        if b:
            print("456")
        else:
            print("789")
    else:
        print("123")
    
    if not a:
        None
```

- **If_AddShortCircuiting**

```python
if a:

if a and (True or False) and (False and True)

if a and ((10 > 5) or (3 < 1))

```

- **StringUnfoldding**

```python
"abcd"

"ab" + "cd"

```

### Multi-mutate

### Python scripts

- `mutators.py`:  Mutator definitions.
- `Mutate.py`: Main function.
- `tmp.py`: Temp file for evaluate the function in dataset.
- `colored_table.py`: Script for coloring the table for further anlysis.

### Testing Results
https://docs.google.com/spreadsheets/d/1yL7ayoBuShTkTuEwIWZKzHYcVFu5u5Rv7GNG-qxscdU/edit?gid=0#gid=0
