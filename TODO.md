## Bugs
## Requirements
1. Multi access point BnB
2. - [x] Add nearest neighbor algorithm
3. Load input file into a list of orders
   1. user can ask for next unfulfilled order
   2. user choose an order number (line of order in file: first line is order number 1)
4. Dynamic start/end locations at any time
   - [x] change graph, distance[(end, start)] = 0 to ensure end to start is connected.
   - [x] every node can not access start, distance[(_, start)] = inf
   - [ ] change at any time
5. The timeout should be a specified by the user via a menu setting in seconds (can be decimal/fractions of a second - i.e. 1, 60, 0.25, etc)
6. - [x] Lazy route(lower turning times)
7. More robust error handling