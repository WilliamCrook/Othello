import tkinter as tk
import numpy as np
import time
import threading

#-----------------------------------------------------------------------------#
'''OPPONENT'''
#-----------------------------------------------------------------------------#

def turn_callback(self, *args):
    global turn
    
    player = turn.get()
    all_moves = []
    
    for child in children:
        all_moves.append(Toggle(child,'check',str(1-player)))
    
    if max(all_moves, key = len) == []:
        threading.Thread(target = lambda: stalemate(player)).start()
    
    elif player == 0:
        all_moves = [x for x in all_moves if x != []]
        threading.Thread(target=lambda: computer_moves(all_moves)).start()

def stalemate(player):
    global turn, children, stalemate_counter
    
    game_over = [x['textvariable'][0] for x in children]
    
    if '2' not in game_over:
        white = game_over.count('1')
        black = game_over.count('0')
        if white > black:
            tk.messagebox.showwarning('Game Over', 'You win.')
        elif black > white:
            tk.messagebox.showwarning('Game Over', 'I win.')
        elif black == white:
            tk.messagebox.showwarning('Game Over', 'It is a draw.')
    elif stalemate_counter == True:
        tk.messagebox.showwarning('Warning', 'Neither of us can go. That is is the game!')
    else:
        stalemate_counter = True
    
        I_you = ['I', 'You']
        your_my = ['your', 'my']
        
        tk.messagebox.showwarning('Warning', I_you[player] + ' cannot go! It is ' + your_my[player] +' turn again.')
        turn.set(1-player)
        

def computer_moves(all_moves):
    global children, turn, deathlist
    
    time.sleep(1)
    
    corners, corner_state = corner_check(all_moves)
    non_death = [x for x in all_moves if x[0] not in deathlist]
    
    if corners != []:
        best_move = corners
    elif len(non_death) != 0:
        for move in non_death:
           best_move = future_sight(move, corner_state)
           if best_move != None: break
           if move == non_death[-1]: best_move = max(non_death, key = len)
    else:
        for move in all_moves:
            best_move = future_sight(move, corner_state)
            if best_move != None: break
            if move == all_moves[-1]: best_move = max(all_moves, key = len)
    
    Flip_squares(best_move)
    turn.set(1)

def corner_check(all_moves):
    global corners
    
    corner_available = []
    corner_state = []
    best_move = []
    
    for n in range(len(corners)):
        corner_available.append(Toggle(children[corners[n]], 'check', '1'))
        losing_corner = Toggle(children[corners[n]], 'check', '0')
        corner_state.append(losing_corner)
        if losing_corner != [] and corner_available[-1] != []:
            best_move = corner_available[-1]
            break
        elif losing_corner != []:
            counteract = [x for x in all_moves if losing_corner[-1] in x]
            if len(counteract) != 0:
                best_move = max(counteract, key = len)
                break
    
    if best_move == [] and len(corners) != 0:
        best_move = max(corner_available, key = len)
    
    return best_move, corner_state

def future_sight(move, corner_state):
    global children, corners
    
    cache_variables = []
    for square in move:
        cache_variables.append(children[square]['textvariable'])
        children[square].config(textvariable = '0_'+str(square))
      
    new_corners = []
    for n in range(len(corners)):
        new_corners.append(Toggle(children[corners[n]], 'check', '0'))
    
    for ind in range(len(move)):
        children[move[ind]].config(textvariable = cache_variables[ind])
    
    if new_corners != corner_state:
        return None
    else:
        return move
        
#-----------------------------------------------------------------------------#
'''BOARD HANDLING'''
#-----------------------------------------------------------------------------#

def Toggle(e,mode,colour):        
    global children
    
    try:
        current = e.widget['textvariable']
    except:
        current = e['textvariable']
        
    if current.startswith('2') == True:
        possible = Finding(int(current[2:]), colour)
        
        if len(possible) != 0 and mode == 'play':
            Flip_squares(possible)
            turn.set(0)
        else:
            return possible
    else:
        return []
        
def Flip_squares(possible):
    global tiles, corners, stalemate_counter
    
    corners = [x for x in corners if x not in possible]
    
    for child in children[possible]:
        bw = turn.get()
        current = child['textvariable']
        child.config(image = tiles[bw], 
                     textvariable = str(bw) + current[1:])
        child.image = tiles[bw]
    
    stalemate_counter = False
                
def Finding(square, colour):
    global matrix, children, possible
    
    possible = []
    counter = 0
    
    view = Make_Matrix(square)

    for row in view:
        state = [None if x == None else children[x]['textvariable'][0] for x in row]
        found = [ind for ind in range(len(state)) if state[ind] == colour]
        for val in found:
            flip = Check_if_valid([view[1][1],row[val]], val, counter, 
                                   colour)
            if flip != None: possible.extend(flip)
        counter += 1
    
    return list(dict.fromkeys(possible))

def Check_if_valid(flip, index, row, colour):
    global children
    
    square = flip[1]
    
    for n in range(7):
        try:
            view = Make_Matrix(square)
            square = view[row][index]
            
            if children[square]['textvariable'][0] == '2':
                return None
            elif children[square]['textvariable'][0] == colour:
                flip.append(square)
                continue
            else:
                flip.append(square)
                return flip
        except:
            return None
    
def Make_Matrix(centre):
    global matrix
    
    view = []
    cols = []
    rows = []
    
    line = [ind for ind in range(8) if centre in matrix[ind]][0]
    index = [ind for ind in range(8) if matrix[line][ind] == centre][0]
    
    if index != 0: cols.append(index - 1)
    else: cols.append(None)
    if index !=7: cols.extend([index, index + 1])
    else: cols.extend([index, None]) 
    
    if line != 0: rows.append(line - 1)
    else: rows.append(None)
    if line != 7: rows.extend([line, line + 1])
    else: rows.extend([line,None]) 
    
    for row in rows:
        if row == None:
            view.append([None,None,None])
        elif cols[0] == None:
            view.append([None,matrix[row][0],matrix[row][1]])
        elif cols[2] == None:
            view.append([matrix[row][6],matrix[row][7],None])
        else:
            view.append(matrix[row][cols])
    
    return view

#-----------------------------------------------------------------------------#
'''START UP'''
#-----------------------------------------------------------------------------#
    
class Start_up():
    def __init__(self, master):
        global tiles, matrix, children
        
        Board = tk.PhotoImage(file = 'F:board.png')
        Frame = tk.Label(master, image = Board, textvariable = 'NaN')
        Frame.pack(anchor = 'nw')
        Frame.image = Board
        xco = 56
        yco = 56
        
        counter = 1
        line = []
        for ind in range(64):
            line.append(counter)
            if counter == 28 or counter == 37: 
                default = tiles[0]
                var = 0
            elif counter == 29 or counter == 36: 
                default = tiles[1]
                var = 1
            else: 
                default = tiles[2]
                var = 2
            
            square = tk.Label(master, image = default, borderwidth = 0, 
                              textvariable = str(var) + '_' + str(counter))
            square.place(x = xco, y = yco)
            square.image = default
            counter += 1
            
            square.bind('<Button-1>', lambda e: Toggle(e,'play','0'))
            
            xco += 84
            if xco == 728:
                matrix.append(line)
                line = []
                xco = 56
                yco += 84
        
        children = np.array(window.winfo_children())
        matrix = np.array(matrix)
    
#-----------------------------------------------------------------------------#
'''GUI'''
#-----------------------------------------------------------------------------#

window = tk.Tk()
window.wm_title("Othello")
window.geometry("777x777")

tiles = [tk.PhotoImage(file = 'F:/black.png'),
         tk.PhotoImage(file = 'F:/white.png'),
         tk.PhotoImage(file = 'F:/empty.png')]
matrix = []
children = []
turn = tk.IntVar(window,value=1)
turn.trace("w",turn_callback)
corners = [1,8,57,64]
deathlist = [2,7,9,10,15,16,49,50,55,56,58,63]
stalemate_counter = False

Start_up(window)
    
window.mainloop()