# Description: A simple tool to merge several pgn games into a single game with
# variations.

import chess.pgn
import sys
import re
import io
from collections import OrderedDict
from itertools import filterfalse


# Extracts annotations from the comment
COLOR_COMMANDS = {"%cal", "%csl"}
SKIP_COMMANDS = {"%eval", "%clk", "%emt"}  # drop these entirely

def extract_annotations(text):
    annotations = OrderedDict()
    normal_text = ""

    parts = re.split(r"\[|\]", text)
    for part in parts:
        if part and part[0] == "%":
            cmd, _, rest = part.partition(" ")
            if cmd in SKIP_COMMANDS:
                continue  # discard eval/clock annotations
            elif cmd in COLOR_COMMANDS:
                values = [v.strip() for v in rest.split(",")]
                if cmd not in annotations:
                    annotations[cmd] = OrderedDict()
                for value in values:
                    if not value:
                        continue
                    annotations[cmd][value[1:]] = value[0]
            else:
                if cmd not in annotations:
                    annotations[cmd] = rest.strip()
        else:
            normal_text += part

    normal_text = re.sub(r"\ ", " ", normal_text)
    return normal_text, annotations

def merge_text_strings(text1, text2):
    # If one is included in the other then it's a duplicate comment and should be ignored
    one_in_two = text1 and text2 and text1.casefold() in text2.casefold()
    two_in_one = text1 and text2 and text2.casefold() in text1.casefold()
    identical = one_in_two and two_in_one

    if identical:
        return text1
    if one_in_two:
        return text2
    if two_in_one:
        return text1
    if text1 and text2:
        transposition = "Transposition: "
        if transposition in text1 or transposition in text2:
            print(f"Found \"{transposition}\" in one of these two comments about to be merged:")
            print(f"Text1: \"{text1}\"")
            print(f"Text2: \"{text2}\"")
            sys.exit()
        return text1 + "\n\n" + text2
    if text1:
        return text1
    if text2:
        return text2
    return ""

# Picks one color of two according to a prio list when two colors are conflicting
def pick_color(color1, color2):
    color_prio = ['R', 'G', 'B', 'Y']    # highest prio first
    if color_prio.index(color1) < color_prio.index(color2):
        return color1
    else:
        return color2

def merge_annotations(annotations1, annotations2):
    COLOR_COMMANDS = {"%cal", "%csl"}

    for cmd2, value2 in annotations2.items():
        if cmd2 not in annotations1:
            annotations1[cmd2] = value2
        elif cmd2 in COLOR_COMMANDS:
            # Existing color-merging logic
            ucis = value2
            for uci in ucis:
                ucis1 = annotations1[cmd2]
                if uci in ucis1:
                    color1 = ucis1[uci]
                    color2 = ucis[uci]
                    ucis1[uci] = pick_color(color1, color2)
                else:
                    ucis1[uci] = ucis[uci]
        # else: non-color command already exists, keep the first value

    formatted_annotations = ""
    for cmd, value in annotations1.items():
        if cmd in COLOR_COMMANDS:
            values = map(lambda uci: "" + value[uci] + uci, value)
            formatted_annotations += f"[{cmd} {','.join(values)}]"
        else:
            formatted_annotations += f"[{cmd} {value}]"

    return formatted_annotations

def merge_comments(text1, text2):
    normal_text1, annotations1 = extract_annotations(text1)
    normal_text2, annotations2 = extract_annotations(text2)

    combined_text = merge_text_strings(normal_text1.strip(), normal_text2.strip())
    combined_annotations = merge_annotations(annotations1, annotations2)

    # Put text and annotations together in one block
    if combined_text and combined_annotations:
        return combined_text + " " + combined_annotations, ""
    elif combined_annotations:
        return combined_annotations, ""
    else:
        return combined_text, ""

def insert_braces(text):
    # Find all the occurrances of the braced string using re.finditer
    brace_matches = list(re.finditer(r'\{(.*?)\}', text, flags=re.DOTALL))

    # Iterate through all the matches (in reversed order because inserting stuff messes up the matches completely)
    for brace_match in reversed(brace_matches):
        start_pos = brace_match.start()
        #end_pos = brace_match.end()    # Assigned but never used

        # Find the position of the first [% within the braces
        percent_match = re.search(r'\[%', brace_match.group(1), flags=re.DOTALL)
        if percent_match is None:
            continue

        percent_pos = percent_match.start() + start_pos + 1

        comment_text = text[start_pos + 1:percent_pos].strip()

        # Insert "} {" at the position of the [% , if and only if the text before is non-empty
        if comment_text:
            text = text[:percent_pos] + "} { " + text[percent_pos:]

    return text

def filterOptions(argument):
    return (re.match("^--[a-zA-Z-]*", argument))

def merge(pgns: list):
    usage = f"Usage: {sys.argv[0]} <PGN FILES>... <OUTPUT FILE> [--no-comments]\nWhere OUTPUT_FILE can be - to indicate STDOUT."

    master_node = chess.pgn.Game()

    games = []
    for line in pgns:
        # pgn = open("\n".join(line), encoding="utf-8")
        pgn = io.StringIO("".join(line))
        game = chess.pgn.read_game(pgn)
        while game is not None:
            text, annotations = merge_comments(master_node.comment, game.comment)

            master_node.comment = f"{text}{annotations}"

            games.append(game)
            game = chess.pgn.read_game(pgn)

    mlist = []
    headers = {}
    for game in games:
        mlist.extend(game.variations)

        # Save all headers from all games
        for header in game.headers.keys():
            if header not in headers:
                headers[header] = set()
            headers[header].add(game.headers[header])

    # Set those headers that had common values in all games
    for header in headers:
        values = headers[header]
        if len(values) == 1:
            value = values.pop()
            master_node.headers[header] = value

    variations = [(master_node, mlist)]
    done = False

    while not done:
        newvars = []
        done = True
        for vnode, nodes in variations:
            newmoves = {}  # Maps move to its index in newvars.
            for node in nodes:
                if node.move is None:
                    continue
                elif node.move not in list(newmoves):
                    nvnode = vnode.add_variation(node.move, nags = node.nags)
                    text, annotations = merge_comments(node.comment, "")


                    nvnode.comment = f"{text}{annotations}"

                    if len(node.variations) > 0:
                        done = False
                    newvars.append((nvnode, node.variations))
                    newmoves[node.move] = len(newvars) - 1
                else:
                    nvnode, nlist = newvars[newmoves[node.move]]
                    text, annotations = merge_comments(nvnode.comment, node.comment)
                    nvnode.comment = f"{text}{annotations}"
                    nvnode.nags.update(node.nags)

                    if len(node.variations) > 0:
                        done = False
                    nlist.extend(node.variations)
                    newvars[newmoves[node.move]] = (nvnode, nlist)
        variations = newvars

    pgn = f"{master_node}"

    
    return pgn
