from tkinter import *
from PIL import ImageTk, Image
from copy import deepcopy

# Castling/ WIN /LOSE /Draw /Checked

class Global():
    def __init__(self, map, dict, root:Tk, imgs, current_player, enpuassant, white_pos, w_king_pos, b_king_pos) -> None:
        self.map = map
        self.dict = dict
        self.root = root
        self.imgs = imgs
        self.current_player = current_player
        self.enpuassant = enpuassant
        self.white_pos = white_pos
        self.w_king_pos = w_king_pos
        self.b_king_pos = b_king_pos

def clean_colors(map):
    for i in range(8):
        for j in range(8):
            if map[i][j] == 'gr' or map[i][j] == 'bl' or map[i][j] == 'ga':
                map[i][j] = "bb" if (i + j) % 2 else "ww"
            elif map[i][j][-2:] == '-r':
                map[i][j] = map[i][j][:2]

def handle_movement(glb:Global, piece_name, i, j):
    if piece_name == "pawn": return
    glb.current_player = [i, j, glb.current_player[2]]
    dir = None
    more_than_one_time = True
    if piece_name == "queen" or piece_name == "king":
        dir = ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1))
        more_than_one_time = piece_name == "queen"
    elif piece_name == "rock":
        dir = ((0, 1), (1, 0), (-1, 0), (0, -1))
    elif piece_name == "bishop":
        dir = ((1, 1), (-1, 1), (1, -1), (-1, -1))
    elif piece_name == "knight":
        dir = ((1, 2), (2, 1), (-1, 2), (2, -1), (1, -2), (-2, 1), (-1, -2), (-2, -1))
        more_than_one_time = False
    for (x, y) in dir:
        n_i, n_j = (i, j)
        while n_i + x < 8 and n_i + x >= 0  and n_j + y < 8 and n_j + y >= 0:
            n_i += x
            n_j += y
            if glb.map[n_i][n_j] == 'ww' or glb.map[n_i][n_j] == 'bb':
                glb.map[n_i][n_j] = 'gr'
                if not more_than_one_time: break
                continue
            if glb.current_player[2] not in glb.dict[glb.map[n_i][n_j]]:
                glb.map[n_i][n_j] += "-r"
            break
    draw(glb)

def handle_pawn_movement(glb:Global, i, j):
    glb.current_player = [i, j, glb.current_player[2]]
    dir = None
    two_move_pos = None
    promote_pos = None
    if glb.white_pos == "down":
        dir, two_move_pos = (-1, 6) if glb.current_player[2] == "white" else (1, 1)
    else:
        dir, two_move_pos = (1, 1) if glb.current_player[2] == "white" else (-1, 6)
    promote_pos = 6 if two_move_pos == 1 else 1
    if j != 0 and len(glb.dict[glb.map[i + dir][j - 1]]) > 5 and glb.current_player[2] not in glb.dict[glb.map[i + dir][j - 1]][0:5]:
        glb.map[i + dir][j - 1] += '-r'
    if j != 7 and len(glb.dict[glb.map[i + dir][j + 1]]) > 5 and glb.current_player[2] not in glb.dict[glb.map[i + dir][j + 1]][0:5]:
        glb.map[i + dir][j + 1] += '-r'
    
    if glb.map[i + dir][j] in ('ww', 'bb'):
        glb.map[i + dir][j] = 'gr' if i != promote_pos else 'bl'
    if (glb.map[i + dir][j] == 'gr') and (i == two_move_pos) and (glb.map[i + 2 * dir][j] in ('ww', 'bb')):
        glb.map[i + 2 * dir][j] = 'gr'
    if glb.enpuassant[0] and (i == promote_pos - 2 * dir):
        if j != 0 and (j - 1 == glb.enpuassant[1]):
            glb.map[i + dir][j - 1] = 'ga' 
        elif j != 7 and (j + 1 == glb.enpuassant[1]):
            glb.map[i + dir][j + 1] = 'ga'

    draw(glb)

def make_move(glb:Global, i, j):
    p_i, p_j = (glb.current_player[0], glb.current_player[1])
    glb.map[i][j] = glb.map[p_i][p_j]
    glb.map[p_i][p_j] = "bb" if (p_i + p_j) % 2 else "ww"
    glb.enpuassant = [False, -1]
    if glb.map[i][j][-1] == 'p' and abs(i - p_i) == 2:
        glb.enpuassant = [True, j]
    elif glb.map[i][j][-1] == 'k':
        if glb.current_player == "white":
            glb.w_king_pos = [i, j]
        else:
            glb.b_king_pos = [i, j]

def handle_enpuassant(map, enpuassant, current_player, i, j):
    p_i, p_j = (current_player[0], current_player[1])
    if p_j - 1 == enpuassant[1]:
        map[p_i][p_j - 1] = 'ww' if (p_i + p_j) % 2 else 'bb'
    if p_j + 1 == enpuassant[1]:
        map[p_i][p_j + 1] = 'ww' if (p_i + p_j) % 2 else 'bb'

def handle_option(glb:Global, piece, i, j):
    color = 'w' if glb.current_player[2] == "black" else 'b'
    glb.map[i][j] = color + (piece[0] if piece != 'knight' else 'n')
    draw(glb)

def show_options(glb:Global, i, j):
    for widget in glb.root.winfo_children():
        widget.destroy()
    pieces = ["queen", "knight", "bishop", "rock"]
    
    glb.root.rowconfigure(0, weight=1)
    for k in range(4):
        glb.root.columnconfigure(k, weight=1)

    for k in range(4):
        frame = Frame(glb.root)
        frame.grid(row=0, column=k, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        button = Button(frame, image=glb.imgs[glb.current_player[2] + '_' + pieces[k]],
                           command=lambda k=k: handle_option(glb, pieces[k], i, j), width=300, height=300)
        button.grid(row=0, column=0, sticky="nsew")
    
def check_move(glb:Global, i, j, color):
    matrix = deepcopy(glb.map)
    p_i, p_j = (glb.current_player[0], glb.current_player[1])
    if color == "gray":
        handle_enpuassant(matrix, glb.enpuassant, glb.current_player, i, j)
    matrix[i][j] = glb.map[p_i][p_j]
    matrix[p_i][p_j] = "bb" if (p_i + p_j) % 2 else "ww"
    new_i, new_j = (glb.w_king_pos) if glb.current_player[2] == "white" else (glb.b_king_pos)
    new_i, new_j = (i, j) if matrix[i][j][-1] == 'k' else (new_i, new_j)
    dir = ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1))
    for x, y in dir:
        n_i, n_j = (new_i, new_j)
        second_attacker = 'r' if (x == 0 or y == 0) else 'b'  
        while n_i + x < 8 and n_i + x >= 0  and n_j + y < 8 and n_j + y >= 0:
            n_i += x
            n_j += y
            if matrix[n_i][n_j] in ('ww', 'bb'):
                continue
            if matrix[n_i][n_j][0] == glb.current_player[2][0]:
                break
            if matrix[n_i][n_j][-1] in ('q', second_attacker):
                return False
            break
    dir = ((1, 2), (2, 1), (-1, 2), (2, -1), (-2, 1), (1, -2), (-2, -1), (-1, -2),
           (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1))
    for x, y in dir:
        n_i, n_j = (new_i, new_j)
        if n_i + x < 8 and n_i + x >= 0  and n_j + y < 8 and n_j + y >= 0:
            n_i += x
            n_j += y
            if matrix[n_i][n_j][0] != glb.current_player[2][0]:
                if (abs(x) == 2 and abs(y) == 2) and matrix[n_i][n_j][-1] == 'n':
                    return False
                elif (abs(x) != 2 and abs(y) != 2) and  matrix[n_i][n_j][-1] == 'k':
                    return False
    move = None
    if glb.white_pos == "down":
        move = -1 if glb.current_player[2] == "white" else 1
    else:
        move = 1 if glb.current_player[2] == "white" else -1
    enemy_pwan = 'b' if glb.current_player[2] == "white" else 'w' + 'p'
    if new_j != 0 and matrix[new_i + move][new_j - 1] == enemy_pwan: return False
    if new_j != 7 and matrix[new_i + move][new_j + 1] == enemy_pwan: return False
    return True

def on_click(glb:Global, piece, i, j):
    clean_colors(glb.map)
    colors = ["red", "green", "blue", "gray"]
    if piece == "white" or piece == "black": 
        draw(glb)
        glb.current_player = [-1, -1, glb.current_player[2]]
        return
    if '_' in piece and piece[0:5] != glb.current_player[2]: 
        draw(glb)
        glb.current_player = [-1, -1, glb.current_player[2]]
        return
    if piece in colors:
        if not check_move(glb, i, j, piece): return
        if piece == "gray":
            handle_enpuassant(glb.map, glb.enpuassant, glb.current_player, i, j)
        elif piece == "blue":
            show_options(glb, i, j)
        make_move(glb, i, j)
        ops_player = "white" if glb.current_player[2] == "black" else "black"
        glb.current_player = [-1, -1, ops_player]
        if piece == "blue": return
        draw(glb)
        return
    piece_name = piece[6:]
    handle_movement(glb, piece_name, i, j)
    if piece_name != "pawn": return
    handle_pawn_movement(glb, i, j)

def draw(glb:Global):
    for widget in glb.root.winfo_children():
        widget.destroy()
    for i in range(8):
        for j in range(8):
            bg_color = "black" if (i + j) % 2 else "white"
            given_value = None
            if glb.map[i][j][-2:] == '-r':
                value = glb.dict[glb.map[i][j][0:2]]
                given_value = "red"
                bg_color = "red"
            else:
                value = glb.dict[glb.map[i][j]]
                given_value = value
            Button(glb.root, image=glb.imgs[value], activebackground=bg_color,
            bg=bg_color, command=lambda i=i, j=j, given_value=given_value: 
            on_click(glb, given_value, i, j)).grid(row=i, column=j)

def init_images():
    imgs = {}
    colors = ["white", "green", "red", "black", "blue", "gray"]
    for i in range(12):
        color = "white" if i < 6 else "black"
        pieces = ["king", "queen", "rock", "bishop", "pawn", "knight"]
        piece = color + "_" + pieces[i % 6]
        pure_img = Image.open(f"./imgs/{piece}.png").resize((100, 100))
        img = ImageTk.PhotoImage(pure_img)
        imgs[piece] = img
    for color in colors:
        pure_img = Image.open(f"./imgs/{color}.png").resize((100, 100))
        img = ImageTk.PhotoImage(pure_img)
        imgs[color] = img
    return imgs

def set_black_and_white(map):
    for i in range(8):
        for j in range(8):
            if map[i][j] != '--': continue
            map[i][j] = "bb" if (i + j) % 2 else "ww"

def run(glb:Global):
    set_black_and_white(glb.map)
    draw(glb)
    glb.root.mainloop()

def check_map_and_get_kings_pos(map):
    b_count = 0
    w_count = 0
    w_pos, b_pos = (None, None)
    for i in range(8):
        for j in range(8):
            if i in (0, 7) and map[i][j][-1] == 'p':
                raise IndexError("pawns can not be on the first and/or last row")
            elif map[i][j] == 'wk':
                w_pos = [i, j]
                if w_count == 1:
                    raise ValueError("You can not have more than one white king")
                w_count += 1
            elif map[i][j] == 'bk':
                b_pos = [i, j]
                if b_count == 1:
                    raise ValueError("You can not have more than one black king")
                b_count += 1
    if w_count == 0:
        raise ValueError("You Don't have White king")
    if  b_count == 0:
        raise ValueError("You Don't have Black king")
    return (w_pos, b_pos)

def main():
    map =  [
        ['--', '--', '--', '--', 'wk', '--', '--', '--'],
        ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
        ['--', '--', '--', 'bl', '--', '--', 'br', 'wp'],
        ['--', 'bp', '--', 'wb', 'wr', '--', 'bp', 'bk'],
        ['--', 'bb', 'wp', '--', 'wr', 'wr', 'bp', 'wp'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['wp', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
    ]
    dict = {
        'wk': "white_king",
        'wp': "white_pawn",
        'wb': "white_bishop",
        'wn': "white_knight",
        'wr': "white_rock",
        'wq': "white_queen",
        'bk': "black_king",
        'bp': "black_pawn",
        'bb': "black_bishop",
        'bq': "black_queen",
        'bn': "black_knight",
        'br': "black_rock",

        'ww': "white",
        'bb': "black",
        'gr': "green",
        'rd': "red",
        'bl': "blue",
        'ga': "gray",
    }
    w_king_pos, b_king_pos = check_map_and_get_kings_pos(map)
    root = Tk()
    imgs = init_images()
    current_player = [-1, -1, "white"]
    enpuassant = [False, -1]
    white_pos = "up"
    glb:Global = Global(map, dict, root, imgs, current_player, enpuassant, white_pos, w_king_pos, b_king_pos)
    run(glb)

if __name__ == "__main__":
    main()