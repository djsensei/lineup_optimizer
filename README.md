lineup_optimizer
================

Optimizes Daily Fantasy Football Lineups

To operate:

1. Sign into FanDuel and browse to a tournament you're interested in playing
2. Copy its url
  * example: https://www.fanduel.com/e/Game/10875

3. In a terminal, in the proper working directory, enter:

```python optimize.py https://www.fanduel.com/e/Game/10875 10```

to return the 10 best lineups for that tournament (and every other one with the
    same roster options)
