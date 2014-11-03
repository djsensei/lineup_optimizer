'''
Selects optimal lineup given initial parameters.

Currently depends on having a properly-formatted csv input file.
    columns: name,team,position_text,salary,points

Next steps: 1) Build a web-scraper to pull stat predictions from various sites.
            2) Build conversion functionality to turn those predictions into
                useable csv files (or pandas dfs)
            3) Import scoring systems and salary caps for various DFS sites,
                integrate into the csv or df creation functionality.
            4) Backtest against previous weeks? Forwardtest with real money!?
'''
import sys
import pandas as pd
import numpy as np
from itertools import combinations


class LineupOptimizer(object):
    def __init__(self, csvfile):
        self.roster_allocation = {'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'K': 1,
                                 'D': 1}
        self.salary_cap = 60000.0
        self.full_df = pd.read_csv(csvfile)
        self.check = self._prep_position_dfs()
        self.cut_list, self.check_list = self._filter_weak_players()

    def _prep_position_dfs(self):
        '''
        splits df of all players into positions.
        Returns a dictionary of position dfs, keyed by position
        '''
        df_dict = {}
        for pos in self.roster_allocation:
            df_dict[pos] = self.full_df[self.full_df['position_text']==pos]
        return df_dict

    def _filter_weak_players(self):
        '''
        Eliminates individual players who are clearly worse than another player
            at their position.
        players_per_position indicates how many players you must roster from
            this group.
        '''
        cut_dict = {}
        check_dict = {}
        for pos in self.check:
            cut_list = []
            check_list = []
            for i1, r1 in self.check[pos].iterrows():
                cut_count = 0
                for i2, r2 in self.check[pos].iterrows():
                    if i1 == i2:
                        continue
                    if r2['salary'] <= r1['salary'] and \
                       r2['points'] >= r1['points']:
                        cut_count += 1
                if cut_count >= self.roster_allocation[pos]:
                    cut_list.append(i1)
                else:
                    check_list.append(i1)
            cut_dict[pos] = cut_list
            check_dict[pos] = check_list
        return cut_dict, check_dict

    def _simple_lineup_score(self, lineup):
        '''
        Just returns the salary and predicted score for a list of players
        '''
        roster = self.full_df.ix[lineup]
        return roster['salary'].sum(), roster['points'].sum()

    def _pos_gen(self, pos):
        '''
        Generates all potential roster combinations for a given position
        '''
        n = self.roster_allocation[pos]
        if n == 1:
            for i in self.check_list[pos]:
                yield i
        else:
            for c in combinations(self.check_list[pos], n):
                yield [c[k] for k in range(n)]

    def _solo_pos_gen(self):
        '''
        Generates all combinations of QB+TE+K+D
        '''
        for qb in self._pos_gen('QB'):
            for te in self._pos_gen('TE'):
                for k in self._pos_gen('K'):
                    for d in self._pos_gen('D'):
                        yield [qb, te, k, d]

    def _filter_combos(self, gen):
        '''
        Using gen (a generator function), create all combos of that type.
        Then filter out the ones that are clearly worse than the others.
        '''
        combos = []
        for combo in gen:
            salary, score = self._simple_lineup_score(combo)
            combos.append((combo, salary, score))
        check_combos = []
        cut_combos = []
        for c1 in combos:
            cut = False
            for c2 in combos:
                if c1 == c2:
                    continue
                if c2[1] <= c1[1] and c2[2] > c1[2]:
                    cut = True
            if not cut:
                check_combos.append(c1)
        return check_combos

    def _split_and_filter_combos(self):
        '''
        Splits the roster into 3 chunks so that the final combinatoric
            optimization is of practical size.
        '''
        solo_combos = self._filter_combos(self._solo_pos_gen())
        rb_combos = self._filter_combos(self._pos_gen('RB'))
        wr_combos = self._filter_combos(self._pos_gen('WR'))
        return solo_combos, rb_combos, wr_combos

    def find_optimal_lineups(self, n=5, verbose=False):
        '''
        Creates a selection of potential player groups:
            (QB+TE+K+D, RB+RB, WR+WR+WR)
        Combinatorically searches all possibilities.
        Returns the n best valid lineups.
        '''
        best = [(None, 0.0)] * n # (lineup, score)
        if verbose:
            print 'loading possible winning combos of solo players, RBs, and \
                   WRs...'
        solos, rbs, wrs = self._split_and_filter_combos()
        if verbose:
            print 'trying all combinations of those combos...'
        for s in solos:
            for r in rbs:
                for w in wrs:
                    lineup = s[0] + r[0] + w[0]
                    salary = s[1] + r[1] + w[1]
                    if salary <= self.salary_cap:
                        score = s[2] + r[2] + w[2]
                        if score > best[-1][1]:
                            # it makes the list!
                            if verbose: print 'I found a better new lineup!'
                            best[-1] = (lineup, score)
                            best = sorted(best, key = lambda x: x[1],
                                          reverse=True)
        return best

    def print_best_lineups(self, best):
        c = self.full_df.columns
        for i, b in enumerate(best):
            print 'BEST LINEUP ', i
            bdf = self.full_df.ix[b[0]]
            for _, r in bdf.iterrows():
                print '   ', r['position_text'], '   ', r[0]

if __name__=='__main__':
    file = sys.argv[1]
    n = int(sys.argv[2])
    linopt = LineupOptimizer(file)
    bests = linopt.find_optimal_lineups(n)
    linopt.print_best_lineups(bests)
