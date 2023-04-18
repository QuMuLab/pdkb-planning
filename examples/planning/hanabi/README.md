# Hanabi

Boardgame Hanabi

## Author

- Chris Yeung

### Maintainer

- Christian Muise <christian.muise@queensu.ca>

## Description

In this game, each player is dealt a set of cards, each with a combination of a number and color. There are normally 5 colors, with each set counting up to 5 (in the original game, there are multiple cards with the same combination to allow for mistakes). The goal of the game is to place the cards of the same color in order from 1 to 5. The catch is that each player can see everyone else's cards but not their own. The game works by each player either giving a hint to another player about one aspect of a single card (either color or number, but not both). Alternatively, the player can play a card instead of giving a hint if they are confident about a particular card they are holding.

In this version of the game, there are no turns and the goal is just to place all the cards in the correct piles and in the right order. The initial game state has 15 cards (1-5 in three colors) and 3 agents. The cards are distributed evenly among all 3 agents. There are 3 actions to play a card or give a number or color hint. A card can only be played if the agent knows they are holding the card and know the color (and number) of the card. When giving a hint, the hint-giver must know the color of the card and that the hint-receiver is holding the card. The effect is that the hint-receiver knows the number or color of the card, and they also know that the hint-giver knows the number or color of the card. It is assumed that everyone in the game also has access to this knowledge (derive-condition is always). The planner is able to find a solution to this problem, although it takes some time.

## Note

Created for CISC 813: Automated Planning, at Queen's University.

## License

MIT License found in the [LICENSE](LICENSE.md) file.







