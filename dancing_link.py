import argparse
import math
class Node:
    def __init__(self, row_index):
        # Initiliase nodes to link to themselves
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.row_index = row_index

    def col_header(self):
        node = self.up
        while (node.row_index != -1):
            node = node.up
        return node


    def remove_from_row(self):
        self.left.right = self.right
        self.right.left = self.left

    def remove_from_col(self):
        self.up.down = self.down
        self.down.up = self.up

    def put_in_row(self):
        self.left.right = self
        self.right.left = self

    def put_in_col(self):
        self.up.down = self
        self.down.up = self


    # Cover clashing columns & rows
    # A column "clashes" with our current row selection if our row covers that column
    # A row clashes with our current row selection if they share overlapping columns
    def cover(self):
        # Loop through all nodes in this row
        node = self.right
        while True:
            col_node = node.down
            while (col_node != node):
                if (col_node.row_index != -1): # Remove clashing row
                    row_node = col_node.right
                    while (row_node != col_node): # We don't actually need to remove col_node itself from its column -- this will help us in our back tracing algorithm.
                        row_node.remove_from_col()
                        row_node = row_node.right
                else:                        # From the column level, only clash to clean up is the column header
                    col_node.remove_from_row()
                col_node = col_node.down

            if (node == self):
                break

            node = node.right
        


    # Reverse covering operation
    def uncover(self):
        # Loop through all the nodes in this row
        node = self.right
        while True:
            col_node = node.down
            while (col_node != node):
                if (col_node.row_index != -1): # Reintroduce clashing rows that have been removed
                    row_node = col_node.right
                    while (row_node != col_node):
                        row_node.put_in_col()
                        row_node = row_node.right
                else:
                    col_node.put_in_row()
                col_node = col_node.down

            if(node == self):
                break

            node = node.right



# Given a non-header node, find the node that should be on its left, by traversing past column headers.
# Return starting node if no other node on the row
def traverse_find_left_node(node):
    row_index = node.row_index
    # Turn node into its column header node
    node = node.col_header()

    # Travsere through column header nodes, and check each column whether it contains a node on the inital row_index
    # Ultimately if it wraps around the whole node map and doesn't find any matches, it will just return initial node
    while True:
        node = node.left
        while True:
            node = node.down
            if node.row_index == row_index:
                return node
            elif node.row_index == -1:
                break


#test_matrix = [[0,0,1,0,1,1,0],[1,0,0,1,0,0,1],[0,1,1,0,0,1,0],[1,0,0,1,0,0,0],[0,1,0,0,0,0,1],[0,0,0,1,1,0,1]]
test_matrix = [[0,1,0,1,0,0],[0,0,1,0,1,0],[1,0,1,0,0,0],[0,1,0,1,0,1],[1,0,0,0,0,1],[1,0,1,0,0,0],[0,1,0,0,1,1]]
class NodeMap:
    def __init__(self, constraint_matrix=test_matrix):
        self.root = Node(-1)
        for col in constraint_matrix:
            self.add_col(col)

    def add_col(self, col):
        col_header = Node(-1)

        # Insert at right most place
        self.root.left.right = col_header
        col_header.left = self.root.left
        self.root.left = col_header
        col_header.right = self.root

        for i in range(len(col)):
            if col[i] == 1:
                curr_node = Node(i)
                col_header.up.down = curr_node
                curr_node.up = col_header.up
                col_header.up = curr_node
                curr_node.down = col_header

                # Search for next column which contains a '1' in same row_index
                left_node = traverse_find_left_node(curr_node)
                left_node.right.left = curr_node
                curr_node.right = left_node.right
                left_node.right = curr_node
                curr_node.left = left_node
    
    def choose_column(self):
        # To be used in each step of dancing link -- pick the column with the least number of 1's, as this is likely to reduce backtracking needed.
        # But for some reason this is causing my code to run slower than before. Let's leave this for now.
        #col_header = self.root.right
        #best_col_header = col_header
        #max_weight = 0
        #while (col_header != self.root):
        #    node = col_header.down
        #    weight = 0
        #    while (node != col_header):
        #        weight += 1
        #        node = node.down
        #    if weight > max_weight:
        #        max_weight = weight
        #        best_col_header = col_header
        #    col_header = col_header.right
        #return best_col_header
        return self.root.right





def dancing_link():
    global node_map
    global solution_set
    if (node_map.root.right == node_map.root):
        global initial_constraint_matrix
        output_sudoku_solution(initial_constraint_matrix, solution_set)
        exit()


    # We are allowed to pick a column. Pick the column with fewest 1's to improve efficiency.
    col_header = node_map.choose_column()

    node = col_header.down
    while (node != col_header):
        # Include this row in partial solution
        solution_set.append(node.row_index)

        # Cover clashing columns + rows
        node.cover()

        # Do dancing link on reduced matrix
        dancing_link()

        # If the code hasn't quit by this time, our row selection isn't correct.
        del solution_set[-1]
        node.uncover()

        node = node.down

    




def cr_transform(sudoku_dimension, col_or_row, value):
    # Sudoku dimension -- e.g. if 9x9, then dimension is 3
    # This represents the constraint "value exists in col_or_row" to be used in exact cover problem
    result = [0] * sudoku_dimension**4
    result[col_or_row * sudoku_dimension**2 + value] = 1
    return result

def s_transform(sudoku_dimension, row, col, value):
    # Sudoku dimension -- e.g. if 9x9, then dimension is 3
    # This represents the constraint "value exists in nth square" to be used in exact cover problem
    result = [0] * sudoku_dimension**4
    s_map = {}
    for i in range(sudoku_dimension):
        tmp = {}
        for j in range(sudoku_dimension):
            tmp[j] = i * sudoku_dimension + j
        s_map[i] = tmp
    result[s_map[row//sudoku_dimension][col//sudoku_dimension] * sudoku_dimension**2 + value] = 1
    return result

def v_transform(sudoku_dimension, row, col):
    # Sudoku dimension -- e.g. if 9x9, then dimension is 3
    # This represents the constraint "sudoku coordinate is populated by some value" to be used in exact cover problem
    result = [0] * sudoku_dimension**4
    result[row * sudoku_dimension**2 + col] = 1
    return result


def construct_sudoku_matrix(sudoku_dimension):
    # Sudoku dimension -- e.g. if 9x9, then dimension is 3
    # Return list of lists, representing a full soduku constraint matrix
    # Sublists to represent rows -- we will further reduce this matrix with the initial constraints later, given the sudoku problem instance
    result = []
    for row in range(sudoku_dimension**2):
        for col in range(sudoku_dimension**2):
            for value in range(sudoku_dimension**2):
                r_constraint = cr_transform(sudoku_dimension, row, value)
                c_constraint = cr_transform(sudoku_dimension, col, value)
                s_constraint = s_transform(sudoku_dimension, row, col, value)
                v_constraint = v_transform(sudoku_dimension, row, col)
                result.append(r_constraint + c_constraint + s_constraint + v_constraint)
    return result

def inverse_transform(sudoku_dimension, r_constraint, c_constraint):
    # Sudoku dimension -- e.g. if 9x9, then dimension is 3
    # Given r_constraint and c_constraint, work out the row & col & value these constraints represent in our sudoku
    row = r_constraint//(sudoku_dimension**2)
    col = c_constraint//(sudoku_dimension**2)
    value = r_constraint % (sudoku_dimension**2)
    return row, col, value


def output_sudoku_solution(initial_constraint_matrix, solution_set):
    global input_data
    global sudoku_dimension
    result = [['.' for col in range(sudoku_dimension**2)] for row in range(sudoku_dimension**2)]
    for row in range(len(input_data)):
        for col in range(len(input_data)):
            value = input_data[row][col]
            if value != ".":
                result[row][col] = value 

    # For each point in the solution set, we can work out the corresponding coordinates and value just by inversing its row transform and col transform, say.
    for solution in solution_set:
        point = initial_constraint_matrix[solution]
        r_constraint = [index for index in range(sudoku_dimension**4) if point[index] == 1][0]
        c_constraint = [index - sudoku_dimension**4 for index in range(sudoku_dimension**4, 2 * sudoku_dimension**4) if point[index] == 1][0]
        row, col, value = inverse_transform(sudoku_dimension, r_constraint, c_constraint)
        result[row][col] = str(value + 1) # Convert back to 1-indexed value

    for row in result:
        print("".join(row))



if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Expecting sudoku input file.")
    parser.add_argument("--input_path", type=str, help="Path to the sudoku input file.", default="sudoku_0")
    args = parser.parse_args()

    with open(args.input_path) as f:
        input_data = f.read().splitlines()
    sudoku_dimension = int(math.sqrt(len(input_data[0])))

    initial_constraint_matrix = construct_sudoku_matrix(sudoku_dimension)

    # Remove rows from constraint matrix based on given information in the sudoku instance, and remove clashing constraints
    for row in range(len(input_data)):
        for col in range(len(input_data)):
            value = input_data[row][col]
            if value != ".":
                value = int(value) - 1 # Turn into zero indexed format for python purposes
                r_constraint = cr_transform(sudoku_dimension, row, value)
                c_constraint = cr_transform(sudoku_dimension, col, value)
                s_constraint = s_transform(sudoku_dimension, row, col, value)
                v_constraint = v_transform(sudoku_dimension, row, col)
                curr_constraint = r_constraint + c_constraint + s_constraint + v_constraint
                initial_constraint_matrix = [constraint for constraint in initial_constraint_matrix if 2 not in [sum(x) for x in zip(curr_constraint, constraint)]]

    # Transpose constraint matrix so we can add individual columns
    constraint_matrix = map(list, zip(*initial_constraint_matrix))

    # Remove zero columns -- these are already satisfied constraints in the sudoku instance
    constraint_matrix = filter(lambda col: 1 in col, constraint_matrix)

    # Transform constraint matrix into node map
    node_map = NodeMap(constraint_matrix)

    # Dancing link steps
    # Make solution_set and node_map accessible by recursive dancing_link function
    solution_set = []
    dancing_link()

    # If we haven't exited code by now, there is no solution
    print("no solution you dummy")


