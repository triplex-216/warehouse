# Warehouse Navigator

## Release Note
- **Final** (06/11/2023)
  - Visual improvements:  
    - Highlight path on map in colors
    - Loading animation

  - Support genetic algorithm. 

  - Speed up branch-and-bound by using Numba JIT when available.

  - Other improvements. 


- **Beta 2.0** (06/01/2023)
  - Support branch-and-bound algorithm with multiple access. 
    - Will fallback to the default algorithm upon timeout. 
  
  - Support reading and processing order lists stored in files
  
  - Redesigned data structure to efficiently calculate graphs
  
- **Beta 0.2** (05/25/2023)
  - Support order lists of multiple items. 
  - Add branch-and-bound algorithm. 
  - Visual improvements. 

- **Alpha 0.1** (05/10/2023)
  Initial release. 

## Get Started
This application requires `Python` 3.10+. 

`numpy` and `psutil` are required. To install: 

```bash
$ pip install -r requirements.txt
```

`numba` is a JIT compiler for Python, and boosts `numpy` operations remarkably. The application works without it, but it is highly recommended. 

```bash
$ pip install numba
```

To run the application:
```bash
$ python main.py
```

If you do not wish to install any libraries, a packaged binary is provided. To run the packaged binary: 

```bash
$ chmod +x ./dist/main
$ ./dist/main # Linux
$ ./dist/main-windows-final.exe # Windows
```
