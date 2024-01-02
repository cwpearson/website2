+++
title = "Using c++ to Solve the Jindosh Riddle Dishonored 2's Dust District"
date = 2023-12-24T10:00:00-0700
description = "Brute-force and depth-first search to solve a variation of an Einstein riddle"
tags = ["c++"]
+++

Without further ado, two solutions are presented here: https://github.com/cwpearson/jindosh-riddle/

## The Puzzle

In the Dust District level of Dishonored 2, the player encounters a riddle like the following:

> At the dinner party were Lady Winslow, Doctor Marcolla, Countess Contee, Madam Natsiou, and Baroness Finch.
>
> The women sat in a row. They all wore different colors and Countess Contee wore a jaunty purple hat. Madam Natsiou was at the far left, next to the guest wearing a blue jacket. The lady in green sat left of someone in red. I remember that green outfit because the woman spilled her beer all over it. The traveler from Dabokva was dressed entirely in white. When one of the dinner guests bragged about her War Medal, the woman next to her said they were finer in Dabokva, where she lived.
> 
> So Lady Winslow showed off a prized Ring, at which the lady from Baleton scoffed, saying it was no match for her Bird Pendant. Someone else carried a valuable Snuff Tin and when she saw it, the visitor from Fraeport next to her almost spilled her neighbor's absinthe. Baroness Finch raised her wine in toast. The lady from Karnaca, full of rum, jumped up onto the table, falling onto the guest in the center seat, spilling the poor woman's whiskey. Then Doctor Marcolla captivated them all with a story about her wild youth in Dunwall.
> 
> In the morning, there were four heirlooms under the table: the War Medal, Diamond, the Bird Pendant, and the Snuff Tin.
>
> But who owned each?

When I encountered this puzzle in the game, there were two things I did not know:

1. This is a variation on something known as the "Einstein Riddle," and there are pen-and-paper techniques for solving it that I did not pursue.
2. The game actually [randomly generates this puzzle](https://dishonored.fandom.com/wiki/The_Jindosh_Riddle) in a mad-libs style for each new game. The progras only work for the particular instance I saw, however they're pretty straightforward to adapt.

## Brute-force Search

The [bf.cpp](https://github.com/cwpearson/jindosh-riddle/blob/master/bf.cpp) program enumerates all possible combinations, and presents any solution that does not violate the rules.

There are six categories of five entries of items: position, name, color, item, city, and drink.
We only care about one position, arranging the women left-to-right, so there are 5! = 120 possible combinations for each category, and 120^5 = 24,883,200,000 total combinations that may need to be checked.
As a back-of-the-envelope matter, if my CPU can do billions of operations per second, and we're judicious about minimizing the number of operations required to generate and check each configuration, this should be possible to do in a "small" amount of time.


Lines 11-15 declare the various values as a flat enum.

```c++
enum : enum_type {
  NATSIOU, CONTEE, FINCH, MARCOLLA, WINSLOW,
  RED, WHITE, GREEN, BLUE, PURPLE,
  MEDAL, TIN, PENDANT, RING, DIAMOND,
  FRAEPORT, DUNWALL, BALETON, DABOKVA, KARNACA,
  WINE, RUM, ABSINTHE, BEER, WHISKEY
};
```
[11-15](https://github.com/cwpearson/jindosh-riddle/blob/2a95c92b1d36ab60cf95d160bad4389de0584cc2/bf.cpp#L10-L16)

The arrangement is represented as 5-element arrays, where index 0 corresponds to the left seat.

```c++
std::array<enum_type, 5> WOMEN  = {NATSIOU, CONTEE, FINCH, MARCOLLA, WINSLOW};
std::array<enum_type, 5> COLORS = {RED, WHITE, GREEN, BLUE, PURPLE};
std::array<enum_type, 5> ITEMS  = {MEDAL, TIN, PENDANT, RING, DIAMOND};
std::array<enum_type, 5> CITIES = {FRAEPORT, DUNWALL, BALETON, DABOKVA, KARNACA};
std::array<enum_type, 5> DRINKS = {WINE, RUM, ABSINTHE, BEER, WHISKEY};
```
For example, the above means *Contee* is in the 2nd seat, wearing *green*, from *Dunwall*, drank *absinthe* and her item is the *snuff tin*.

The implementation is relatively straightforward. 
[Lines 87-168](https://github.com/cwpearson/jindosh-riddle/blob/2a95c92b1d36ab60cf95d160bad4389de0584cc2/bf.cpp#L87-L168) define the fourteen rules that are given in the clue.
Each rule is a function that returns `true` iff the rule is satisfied.
The rules work by finding the seat position of a woman (or color, or item, etc) and comparing it to the position of another thing.

The loop to generate all permutaitons looks like this:

```c++
  do {
    do {
      do {
        do {
          do {
            // continue if any rules violated
            // print state otherwise
          } while (std::next_permutation(DRINKS.begin(), DRINKS.end()));
        } while (std::next_permutation(CITIES.begin(), CITIES.end()));
      } while (std::next_permutation(ITEMS.begin(), ITEMS.end()));
    } while (std::next_permutation(COLORS.begin(), COLORS.end()));
  } while (std::next_permutation(WOMEN.begin(), WOMEN.end()));
```
[L188-217](https://github.com/cwpearson/jindosh-riddle/blob/2a95c92b1d36ab60cf95d160bad4389de0584cc2/bf.cpp#L188-L217).

`do...while` is used because `std::next_permutation` produces the next lexicographical permutation of a container, and returns true if there is *another* new permutation to follow on the *next* call to `std::next_permutation`.
The initial entry into the nested loop tests the starting permutation.

The solutions is printed thusly:

```
  NATSIOU    FINCH   CONTEE MARCOLLA  WINSLOW
      TIN    MEDAL  PENDANT  DIAMOND     RING
  DABOKVA FRAEPORT  BALETON  DUNWALL  KARNACA
 ABSINTHE     WINE  WHISKEY     BEER      RUM
    WHITE     BLUE   PURPLE    GREEN      RED
```

On my M1 Mac Air, this generates and checks approximately 100M permutations per second, plenty faste enough to search through 24B permutations in a couple minutes.
In practice, the correct solution is the `1315376933`rd one, so it only takes a dozen seconds or so.

## Depth-first Search

The other solution is in [dfs.cpp](https://github.com/cwpearson/jindosh-riddle/blob/master/dfs.cpp), a depth-first search to find a valid configuration.
The major issue with the brute-force version is that there is no practical way to exclude entire groups of arrangements that all violate the same rule.
For example, any solution where *green* is not directly to the left of *red* is wrong, and need not ever be checked:

```c++
woman:   ?      ?      ?      ?     ?
item:    ?      ?      ?      ?     ?
city:    ?      ?      ?      ?     ?
drink:   ?      ?      ?      ?     ?
color:   ?      ?    RED  GREEN     ?
```

The brute-force version will methodically generate and check all `120^4 * 6 = 1.24B` soltutions where red and green are in the above positions, even though all we need to know is that red and green are in the above positions to know they are all wrong.
At 100M permutations per second, that's 12 seconds.

The depth-first search implementation avoids this problem by modeling a tree of permutations, and excluding entire subtrees when a parent violates any rule.
This leads to two key differences:

1. how permutations are generated
2. how rules must be implemented (to tolerate incomplete arrangements)

### Generating permutations

The depth-first search is inspired by game trees.
In a game tree (e.g. chess), the tree represents all possible board states, rooted at the starting board.
Each node is a board state, and the children of that node are the next possible board states after a single move.
For example, the root node is the starting board, and the children of the root node are the board following each of white's possible first moves - this can mean many children, which is fine.
Each of those nodes has children corresponding to black's first move, each of *those* nodes has children corresponding to white's second move, and so on.
The chess program will search down this tree to find a desirable sequence of moves - if I am white, and the computer is black, it will look for board states where black is winning, and make the moves that lead towards them.

The depth-first search for the Jindosh Puzzle treats the puzzle as a single-player game, where each "move" is to place a woman (or item, color, etc.) into an empty spot.
If a rule is violated by that placement, that would be like making a chess move where the computer loses; a situation to be avoided.
If we manage to search all the way down the tree to a complete permutation where no rules are violated, we've found a solution.

There is a subtle consequence of this design: in chess, it is possible to take multiple paths through the game to the same board position.
As a dumb example, I could move my queen up, and then back, or left, and then back, to get to where I started.
The same is possible for the riddle. For example:

1. Contee in 0, red in 0, green in 1.
2. Contee in 0, green in 1, red in 0.

In chess, this is just a consequence of the rules, and the dept-first search must tolerate this to acurately model the game state.
For our purposes, this just creates redundant permutations to check and should be avoided - the subtress of both of these permutations are identical, so there's no point in generating and checking both nodes - only one is needed.

Permutations are modeled the same way, but an additional `UNKNOWN` enum is added to represent an as-yet unchosen woman (item, city, etc.).

The initial state is now 

```c++
women = {UNKNOWN};
colors = {UNKNOWN};
items = {UNKNOWN};
cities = {UNKNOWN};
drinks = {UNKNOWN};
```
[L72-78](https://github.com/cwpearson/jindosh-riddle/blob/2a95c92b1d36ab60cf95d160bad4389de0584cc2/dfs.cpp#L72-L78)

### Rules that tolerate incomplete arrangements

The main advantage of this approach is it potentially allows entire subtrees to be excluded, but the rule logic has to be rewritten to tolerate `UNKNOWN` entries in the permutation.
In the brute-force search, we are always checking a complete configuration, so the rules are simple.
For example, if green is not directly to the left of red, this is invalid.
In the depth-first search, this rule becomes a failure when

1. `GREEN` and `RED` are present, and `GREEN` is not to the left of `RED` (the brute-force forumulation)
2. `GREEN` is present, and a non-`UNKNOWN`, non-`RED` entry is to the right of it
3. `RED` is present and a non-`UNKNOWN`, non-`GREEN` entry is to the left of it.

It is possible to have a correct implementation with just the original formulation, but time will be spent checking permutations that could otherwise be known to be invalid.

### DFS Performance

On my M1 Mac Air, `dfs` prints this after about 10ms (1200x speedup)

```
SUCCESS! (checked 5356 arrangements, exluded 3490 subtrees)
  NATSIOU    FINCH   CONTEE MARCOLLA  WINSLOW
      TIN    MEDAL  PENDANT  DIAMOND     RING
  DABOKVA FRAEPORT  BALETON  DUNWALL  KARNACA
 ABSINTHE     WINE  WHISKEY     BEER      RUM
    WHITE     BLUE   PURPLE    GREEN      RED
DONE (checked 16783 arrangements, exluded 10941 subtrees)
```

The rules were applied to 5356 arrangements, and excluded 3409 subtrees before the correct solution was found.
Overall, the rules were only applied to 16783 arrangements to exhastively search the entire space of arrangements.
This is compared to the brute-force search, which would need to check 24B arrangements for an exhaustive search.

## An addendum

The third rule in the clue is this:

> The lady in green sat left of someone in red

A strict reading of this rule suggests that the woman in green is *somewhere* to the left of the woman in red, i.e., not necessarily directly next to her.
However, that yields 7 valid solutions. 
If we instead read the rule to mean the woman in green is directly to the left of the woman in red, there is a single solution.
