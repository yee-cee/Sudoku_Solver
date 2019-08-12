#!/usr/bin/env python
#coding:utf-8

"""
Each sudoku board is represented as a dictionary with string keys and
int values.
e.g. my_board['A1'] = 8
"""
import time
from heapq import heappush, heappop
import itertools
import sys

ROW = "ABCDEFGHI"
COL = "123456789"
ROW_IDX = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'I':8}
COL_IDX = {'1':0, '2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7, '9':8}

# Define a priority queue for update
class PriorityQueue(object):
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.REMOVED = '<removed-task>'
        self.counter = itertools.count()

    def add_task(self, task, priority):
        'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heappush(self.pq, entry)

    def remove_task(self, task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def get_priority(self, task):
        return self.entry_finder[task][0]

    def empty(self):
        return len(self.entry_finder) == 0

    def pop_task(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, task = heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')


def get_arc(idx):
    """Get constraint related positions"""

    row_arc = [(idx[0] + COL[c]) for c in range(9)]
    col_arc = [(ROW[r] + idx[1]) for r in range(9)]

    i = ROW.index(idx[0]) // 3 * 3
    j = COL.index(idx[1]) // 3 * 3

    box_arc = [(ROW[r] + COL[c]) for r in range(i, i + 3) for c in range(j, j + 3)]
    return set(row_arc + col_arc + box_arc) - set([idx])


def board2rv(board):
    for r in range(9):
        for c in range(9):
            index = ROW[r] + COL[c]
            value = board[index]

            if value == 0:
                used_values = set([board[unit] for unit in get_arc(index)])
                set_domain(index, set(range(1, 10)) - used_values)
            else:
                domain[index] = set([value])


def set_value(board, idx, val):
    """set a value for one position and delete remaining value in heap"""
    board[idx] = val
    domain[idx] = set([val])
    if idx in remain_value_lookup:
        remain_value_lookup[idx][1] = 0
        del remain_value_lookup[idx]


def set_domain(idx, dom):
    """Set domain for one position and update remaining value in heap"""
    domain[idx] = dom
    rv_entry = [len(dom), idx]
    if idx in remain_value_lookup:
        remain_value_lookup[idx][1] = 0
    remain_value_lookup[idx] = rv_entry

    heappush(remain_value, rv_entry)

def print_board(board):
    """Helper function to print board in a square."""
    print("-----------------")
    for i in ROW:
        row = ''
        for j in COL:
            row += (str(board[i + j]) + " ")
        print(row)


def board_to_string(board):
    """Helper function to convert board dictionary to string for writing."""
    ordered_vals = []
    for r in ROW:
        for c in COL:
            ordered_vals.append(str(board[r + c]))
    return ''.join(ordered_vals)


def area_idx(r, c):
    area_r = int(ROW_IDX[r]/3)
    area_c = int(COL_IDX[c]/3)
    return area_r*3 + area_c


def init_params(board):
    solved_board = {}
    unassign_row = {}
    unassign_col = {}
    unassign_area = {}
    unassign = {}

    for R in ROW:
        unassign_row[R] = set()
    
    for C in COL:
        unassign_col[C] = set()
    
    for A in range(9):
        unassign_area[A] = set()

    for entry in board.keys():
        r = entry[0]
        c = entry[1]
        area = area_idx(r,c)
        solved_board[entry] = board[entry]
        if board[entry] == 0:
            unassign_row[r].add(entry)
            unassign_col[c].add(entry)
            unassign_area[area].add(entry)
            unassign[entry] = set([1,2,3,4,5,6,7,8,9])
    
    for entry in board.keys():
        if board[entry] != 0:
            _, deleted = forward_checking(unassign_row, unassign_col, unassign_area, unassign, entry, board)
            for dlt in deleted:
                unassign[dlt].remove(board[entry])

    return solved_board, unassign_row, unassign_col, unassign_area, unassign        

"""def forward_checking(idx, val):
    Forward checking when assign a value for one position
    changed = []

    for target in get_arc(idx):
        target_domain = domain[target]
        if val in target_domain:
            if len(target_domain) == 1:
                return False, changed
            target_domain.remove(val)
            set_domain(target, target_domain)
            changed.append(target)
    return True, changed  """



"""def backtracking(board):
    #Takes a board and returns solved board.

    idx = None
    while remain_value:
        rv, idx = heappop(remain_value)
        if idx is not None:
            break
    if not remain_value and idx is None:
        return board_to_string(board)

    old_domain = domain[idx]

    for val in old_domain:
        set_value(board, idx, val)
        consistent, changed = forward_checking(idx, val)
        if consistent and backtracking(board) is not None:
            return board_to_string(board)
        for target in changed:
            domain[target].add(val)
            set_domain(target, domain[target])

    board[idx] = 0
    set_domain(idx, old_domain)
    return None """

def forward_checking(unassign_row, unassign_col, unassign_area, unassign, entry, board):
    r = entry[0]
    c = entry[1]
    area = area_idx(r,c)
    value = board[entry]
    deleted = set()

    for row_et in unassign_row[r]:
        if value in unassign[row_et]:
            if len(unassign[row_et]) > 1:
                deleted.add(row_et)
            else:
                return True, None
    
    for col_et in unassign_col[c]:
        if value in unassign[col_et]:
            if len(unassign[col_et]) > 1:
                deleted.add(col_et)
            else:
                return True, None
    
    for area_et in unassign_area[area]:
        if value in unassign[area_et]:
            if(len(unassign[area_et]) > 1):
                deleted.add(area_et)
            else:
                return True, None
    
    return False, deleted


def backtrace(solved_board, unassign_row, unassign_col, unassign_area, unassign, queue):
    if len(unassign) == 0:
        return True
    
    entry = queue.pop_task()
    r = entry[0]
    c = entry[1]
    area = area_idx(r,c)

    unassign_row[r].remove(entry)
    unassign_col[c].remove(entry)
    unassign_area[area].remove(entry)
    values = unassign[entry]
    unassign.pop(entry)

    for value in values:
        solved_board[entry] = value
        fail, delete = forward_checking(unassign_row, unassign_col, unassign_area, unassign, entry, solved_board)
        if not fail:
            for dlt in delete:
                unassign[dlt].remove(value)
                queue.add_task(dlt, len(unassign[dlt]))
            result = backtrace(solved_board, unassign_row, unassign_col, unassign_area, unassign, queue)
            if result:
                return True
            for dlt in delete:
                unassign[dlt].add(value)
                queue.add_task(dlt, len(unassign[dlt]))
    
    unassign_row[r].add(entry)
    unassign_col[c].add(entry)
    unassign_area[area].add(entry)
    unassign[entry] = values
    
    return False
    

def backtracking(board):
    """Takes a board and returns solved board."""
    # TODO: implement this
    
    solved_board, unassign_row, unassign_col, unassign_area, unassign = init_params(board)
    queue = PriorityQueue()
    for entry in unassign.keys():
        queue.add_task(entry, len(unassign[entry]))

    backtrace(solved_board, unassign_row, unassign_col, unassign_area, unassign, queue)

    
    return solved_board


if __name__ == '__main__':

    line = sys.argv[1]
    # Parse boards to dict representation, scanning board L to R, Up to Down
    board = { ROW[r] + COL[c]: int(line[9*r+c])
            for r in range(9) for c in range(9)}
    start = time.time()
    solved_board = backtracking(board)
    end = time.time()
    outputline = board_to_string(solved_board)

    out_filename = 'output.txt'
    outfile = open(out_filename, "w")
    outfile.write(outputline)

    print_board(solved_board)
    print(outputline)
    print(f"Time: {end-start:0.5f}s")