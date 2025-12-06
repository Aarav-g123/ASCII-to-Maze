#!/usr/bin/env python3

import sys
import argparse
from PIL import Image

def image_to_maze(input_path, output_path, width=200, height=200, threshold=128,
                  invert=False, start_pos=None, end_pos=None, add_border=True):
    
    print(f"Loading image: {input_path}")
    img = Image.open(input_path)
    img = img.convert('L')
    img = img.resize((width, height), Image. Resampling. LANCZOS)
    
    pixels = img.load()
    maze = []
    
    for y in range(height):
        row = []
        for x in range(width):
            pixel_value = pixels[x, y]
            if invert:
                is_wall = pixel_value >= threshold
            else:
                is_wall = pixel_value < threshold
            row.append('#' if is_wall else '.')
        maze.append(row)
    
    if add_border:
        for x in range(width):
            maze[0][x] = '#'
            maze[height - 1][x] = '#'
        for y in range(height):
            maze[y][0] = '#'
            maze[y][width - 1] = '#'
    
    if start_pos:
        sx, sy = start_pos
    else:
        sx, sy = find_passage_near(maze, 1, 1, width, height)
    
    if sx is not None and maze[sy][sx] == '.':
        maze[sy][sx] = '>'
        print(f"Start position: ({sx}, {sy})")
    else:
        print("Warning: Could not place start position!")
    
    if end_pos:
        ex, ey = end_pos
    else:
        ex, ey = find_passage_near(maze, width - 2, height - 2, width, height, reverse=True)
    
    if ex is not None and maze[ey][ex] == '.':
        maze[ey][ex] = 'F'
        print(f"End position: ({ex}, {ey})")
    else:
        print("Warning: Could not place end position!")
    
    print(f"Writing maze to: {output_path}")
    with open(output_path, 'w') as f:
        f.write("Type: WarwickMaze\n")
        f.write("Version: 1.0\n")
        f.write(f"Width: {width}\n")
        f.write(f"Height: {height}\n")
        f.write("HeaderEnd\n")
        
        for row in maze:
            f. write(''.join(row) + '\n')
    
    wall_count = sum(row.count('#') for row in maze)
    passage_count = sum(row.count('. ') for row in maze)
    total = width * height
    print(f"\nMaze statistics:")
    print(f"  Dimensions: {width} x {height}")
    print(f"  Walls: {wall_count} ({100*wall_count/total:.1f}%)")
    print(f"  Passages: {passage_count} ({100*passage_count/total:. 1f}%)")


def find_passage_near(maze, target_x, target_y, width, height, reverse=False):
    max_dist = max(width, height)
    
    for dist in range(max_dist):
        for dy in range(-dist, dist + 1):
            for dx in range(-dist, dist + 1):
                if abs(dx) != dist and abs(dy) != dist:
                    continue
                
                x = target_x + dx
                y = target_y + dy
                
                if 0 < x < width - 1 and 0 < y < height - 1:
                    if maze[y][x] == '.':
                        return x, y
    
    return None, None


def preview_maze(maze_path, preview_width=80):
    print("\nMaze preview:")
    print("-" * preview_width)
    
    with open(maze_path, 'r') as f:
        lines = f. readlines()
    
    maze_lines = []
    in_maze = False
    for line in lines:
        if in_maze:
            maze_lines.append(line. rstrip())
        elif line.strip() == "HeaderEnd":
            in_maze = True
    
    if not maze_lines:
        print("Could not read maze data")
        return
    
    height = len(maze_lines)
    width = len(maze_lines[0]) if maze_lines else 0
    
    scale_x = max(1, width // preview_width)
    scale_y = max(1, height // (preview_width // 2))
    
    for y in range(0, height, scale_y):
        row = ""
        for x in range(0, width, scale_x):
            if y < len(maze_lines) and x < len(maze_lines[y]):
                char = maze_lines[y][x]
                if char == '#':
                    row += '█'
                elif char == '>':
                    row += 'S'
                elif char == 'F':
                    row += 'E'
                else:
                    row += ' '
        print(row)
    
    print("-" * preview_width)


def main():
    parser = argparse.ArgumentParser(description='Convert an image to a WarwickMaze file.')
    
    parser.add_argument('input', help='Input image file')
    parser.add_argument('output', nargs='?', default=None, help='Output maze file')
    parser.add_argument('width', nargs='?', type=int, default=200)
    parser.add_argument('height', nargs='?', type=int, default=200)
    parser.add_argument('--threshold', '-t', type=int, default=128)
    parser.add_argument('--invert', '-i', action='store_true')
    parser. add_argument('--no-border', action='store_true')
    parser.add_argument('--start', '-s', type=str, default=None)
    parser.add_argument('--end', '-e', type=str, default=None)
    parser.add_argument('--preview', '-p', action='store_true')
    parser.add_argument('--preview-width', type=int, default=80)
    
    args = parser.parse_args()
    
    if args.output is None:
        base_name = args. input.rsplit('. ', 1)[0]
        args. output = base_name + '.warwickmaze'
    
    if not args.output. endswith('.warwickmaze'):
        args.output = args.output. rsplit('.', 1)[0] + '. warwickmaze'
    
    start_pos = None
    end_pos = None
    
    if args.start:
        try:
            start_pos = tuple(map(int, args.start.split(',')))
        except ValueError:
            print(f"Error: Invalid start position: {args.start}")
            sys.exit(1)
    
    if args.end:
        try:
            end_pos = tuple(map(int, args.end. split(',')))
        except ValueError:
            print(f"Error: Invalid end position: {args.end}")
            sys. exit(1)
    
    try:
        image_to_maze(
            args.input,
            args.output,
            width=args.width,
            height=args. height,
            threshold=args.threshold,
            invert=args.invert,
            start_pos=start_pos,
            end_pos=end_pos,
            add_border=not args.no_border
        )
        
        if args. preview:
            preview_maze(args. output, args.preview_width)
        
        print("\nDone!")
        
    except FileNotFoundError:
        print(f"Error: Could not find: {args.input}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys. exit(1)


if __name__ == '__main__':
    main()