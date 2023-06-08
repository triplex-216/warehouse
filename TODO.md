## Bugs
## Requirements
1. - [x] Multi access point BnB
2. - [x] Add nearest neighbor algorithm
3. - [x] Load input file into a list of orders
   1. user can ask for next unfulfilled order
   2. user choose an order number (line of order in file: first line is order number 1)
4. - [x] Dynamic start/end locations at any time
   - [x] change graph, distance[(end, start)] = 0 to ensure end to start is connected.
   - [x] every node can not access start, distance[(_, start)] = inf
   - [x] change at any time
5. - [x] The timeout should be a specified by the user via a menu setting in seconds (can be decimal/fractions of a second - i.e. 1, 60, 0.25, etc)
6. - [x] Lazy route(lower turning times)
7. More robust error handling
8. - [x] Visiting An->Bn/Be generates the same matrix, since Bn/Be rows won't be blanked out when An->Bn/Be happens. i.e. Only blank out the A->B portion, and don't mess with the B row
9.  - [x] Process longer (lower in tree, closer to complete cycle) tree nodes first (add another priority value to be compared before _index)
10. - [x] Consider the final trip from the last AP, back to the init AP