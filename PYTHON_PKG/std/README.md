# zuu


## Supported Sub Packages
- va (vision and automation)
- app (app configs and automation)
- cli (command line interface)
- doc (documents)
- ext1 
- alpha (for testing purposes)

## install
for plain package
```bash
pip install zuu
```

for sub packages
```bash
pip install zuu[{va, app, cli, ext1, ...}]
```

## Project Layout
| pkg  |    uses     | reserved |
| ---- | ----------- | -------- |
| std  | common, pkg | io       |
| app  | app         |          |
| cli  | common      |          |
| doc  | app, common |          |
| ext1 | pkg         |          |
| va   | pkg         |          |
