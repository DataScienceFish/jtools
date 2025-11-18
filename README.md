# JTools: simple tools, easy life


## Building

```cmd

python setup.py sdist bdist_wheel
twine upload dist/*
```

## Pushing

+ switch to master branch before any changes;

+ git through github-desktop (**AFTER VERSION NUMBER CHANGED**);

+ switch to release branch and run `git merge master`;

+ push through github-desktop

+ switch back to master


## Logging

+ v0.1.8:
  + add: get_next_trddt

+ v0.1.7:
  + update:
    + get_last_trddt: with n option

+ v0.1.6:
  + fix: trading dates funcs
  + add: is_trading_date