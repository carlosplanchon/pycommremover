# pycommremover
*Python3 Module to convert from duration to date and time.*

## Installation
### Install with pip
```
pip3 install -U pycommremover
```

## Usage
```
In [1]: import pycommremover

In [2]: text = """
print("First line")

\"\"\"

print("Commented line.")

'''
print("Commented line 2.")

print("Commented line 3.")

# Single line comment 1.
'''

# Single line comment.
print("Commented line 4.")

\"\"\"

# Single line comment 2.

print("Commented line 5")
"""

In [3]: output = pycommremover.remove_comments(text=text)


In [4]: print(output)

print("First line")





print("Commented line 5")


```
