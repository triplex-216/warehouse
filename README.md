# Warehouse Navigator

## Release Note
- **Beta 2.0** (06/01/2023)
  - Support Branch-and-bound algorithm with multiple access. 
    - Will fall-back to the default algorithm upon timeout. 
  
  - Support reading and processing order lists stored in files
  
  - Redesigned data structure to efficiently calculate graphs
  
- **Beta 0.2** (05/25/2023)
  - Support order lists of multiple items. 
  - Add branch-and-bound algorithm. 
  - Visual improvements. 

- **Alpha 0.1** (05/10/2023)
  Initial release. 

## Get Started
This application requires `Python` 3.10+ and `numpy`. 

To run the application:
```bash
$ cd path-to-binary
$ ./main-linux

# Or if Python is installed on the machine
$ python main.py
```
## Features
- ASCII-encoded text portrayal of the warehouse map. 
  - Add number along axes for better readability. 
  - Highlight paths with arrows. 
- Step-by-step instruction in English. 
