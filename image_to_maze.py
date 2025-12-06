import sys
import argparse
from collections import deque
from PIL import Image, ImageFilter, ImageEnhance



def image_to_maze(input_path, output_path, size=200, threshold=128,
                  invert=False, start_pos=None, end_pos=None, sharpen=True):
    
    print(f"Loading image: {input_path}")
    img = Image.open(input_path)
    img = img.convert('L')
    
    if sharpen:
        img = img.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer. enhance(1.5)
    
    orig_width, orig_height = img.size
    
    if orig_width > orig_height:
        new_width = size
        new_height = int(size * orig_height / orig_width)
    else:
        new_height = size
        new_width = int(size * orig_width / orig_height)
    
    new_width = max(10, min(200, new_width))
    new_height = max(10, min(200, new_height))
    
    img = img.resize((new_width, new_height), Image. Resampling. LANCZOS)
    
    width = new_width
    height = new_height
    
    pixels = img.load()
    maze = []
    
    for y in range(height):
        row = []
        for x in range(width):
            pixel_value = pixels[x, y]
            if invert:
                is_wall = pixel_value < threshold
            else:
                is_wall = pixel_value >= threshold
            row.append('#' if is_wall else '.')
        maze.append(row)
    
    for x in range(width):
        maze[0][x] = '#'
        maze[height - 1][x] = '#'
    for y in range(height):
        maze[y][0] = '#'
        maze[y][width - 1] = '#'
    
    passages = get_all_passages(maze, width, height)
    
    if len(passages) < 2:
        print("Not enough passages, trying inverted threshold...")
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                pixel_value = pixels[x, y]
                if invert:
                    is_wall = pixel_value >= threshold
                else:
                    is_wall = pixel_value < threshold
                maze[y][x] = '#' if is_wall else '.'
        passages = get_all_passages(maze, width, height)
    
    if len(passages) < 2:
        print("Still not enough passages, creating some...")
        maze = create_passages(maze, width, height)
        passages = get_all_passages(maze, width, height)
    
    if start_pos and end_pos:
        sx, sy = start_pos
        ex, ey = end_pos
    else:
        print("Finding longest existing path...")
        result = find_longest_path_endpoints(maze, width, height)
        if result:
            sx, sy, ex, ey = result
            print(f"Found path with endpoints at ({sx},{sy}) and ({ex},{ey})")
        else:
            print("No existing path found, forcing endpoints...")
            sx, sy, ex, ey = force_start_end(maze, width, height)
    
    path_exists = bfs_path_exists(maze, sx, sy, ex, ey, width, height)
    
    if not path_exists:
        print("No path exists, carving one...")
        maze = carve_path_smart(maze, sx, sy, ex, ey, width, height)
    
    maze[sy][sx] = '>'
    maze[ey][ex] = 'F'
    
    print(f"Start position: ({sx}, {sy})")
    print(f"End position: ({ex}, {ey})")
    
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
    passage_count = width * height - wall_count
    total = width * height
    wall_pct = 100.0 * wall_count / total
    passage_pct = 100.0 * passage_count / total
    print(f"\nMaze statistics:")
    print(f"  Dimensions: {width} x {height}")
    print(f"  Walls: {wall_count} ({wall_pct:.1f}%)")
    print(f"  Passages: {passage_count} ({passage_pct:.1f}%)")


def get_all_passages(maze, width, height):
    passages = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == '. ':
                passages. append((x, y))
    return passages


def find_connected_components(maze, width, height):
    visited = set()
    components = []
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == '.' and (x, y) not in visited:
                component = []
                queue = deque([(x, y)])
                visited.add((x, y))
                
                while queue:
                    cx, cy = queue.popleft()
                    component.append((cx, cy))
                    
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 < nx < width - 1 and 0 < ny < height - 1:
                            if (nx, ny) not in visited and maze[ny][nx] == '.':
                                visited.add((nx, ny))
                                queue.append((nx, ny))
                
                components. append(component)
    
    return components


def find_longest_path_endpoints(maze, width, height):
    components = find_connected_components(maze, width, height)
    
    if not components:
        return None
    
    largest = max(components, key=len)
    
    if len(largest) < 2:
        return None
    
    start = largest[0]
    farthest_from_start, _ = bfs_farthest(maze, start[0], start[1], width, height)
    
    if farthest_from_start is None:
        return None
    
    farthest_from_that, dist = bfs_farthest(maze, farthest_from_start[0], farthest_from_start[1], width, height)
    
    if farthest_from_that is None:
        return None
    
    print(f"Longest path distance: {dist}")
    
    return (farthest_from_start[0], farthest_from_start[1], 
            farthest_from_that[0], farthest_from_that[1])


def bfs_farthest(maze, sx, sy, width, height):
    visited = {(sx, sy): 0}
    queue = deque([(sx, sy, 0)])
    farthest = (sx, sy)
    max_dist = 0
    
    while queue:
        x, y, dist = queue.popleft()
        
        if dist > max_dist:
            max_dist = dist
            farthest = (x, y)
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1:
                if (nx, ny) not in visited and maze[ny][nx] == '.':
                    visited[(nx, ny)] = dist + 1
                    queue.append((nx, ny, dist + 1))
    
    return farthest, max_dist


def force_start_end(maze, width, height):
    sx = 2
    sy = 2
    ex = width - 3
    ey = height - 3
    
    sx = max(1, min(sx, width - 2))
    sy = max(1, min(sy, height - 2))
    ex = max(1, min(ex, width - 2))
    ey = max(1, min(ey, height - 2))
    
    maze[sy][sx] = '.'
    maze[ey][ex] = '.'
    
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            ny, nx = sy + dy, sx + dx
            if 0 < nx < width - 1 and 0 < ny < height - 1:
                maze[ny][nx] = '.'
            ny, nx = ey + dy, ex + dx
            if 0 < nx < width - 1 and 0 < ny < height - 1:
                maze[ny][nx] = '.'
    
    return sx, sy, ex, ey


def bfs_path_exists(maze, sx, sy, ex, ey, width, height):
    if sy >= len(maze) or sx >= len(maze[0]):
        return False
    if ey >= len(maze) or ex >= len(maze[0]):
        return False
    if maze[sy][sx] == '#' or maze[ey][ex] == '#':
        return False
    
    visited = set()
    queue = deque([(sx, sy)])
    visited.add((sx, sy))
    
    while queue:
        x, y = queue. popleft()
        
        if x == ex and y == ey:
            return True
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited and maze[ny][nx] != '#':
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    
    return False


def carve_path_smart(maze, sx, sy, ex, ey, width, height):
    visited = {(sx, sy): None}
    queue = deque([(sx, sy)])
    
    while queue:
        x, y = queue.popleft()
        
        if x == ex and y == ey:
            break
        
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1:
                if (nx, ny) not in visited:
                    cost = 0 if maze[ny][nx] == '.' else 1
                    neighbors.append((cost, nx, ny))
        
        neighbors.sort()
        
        for cost, nx, ny in neighbors:
            if (nx, ny) not in visited:
                visited[(nx, ny)] = (x, y)
                queue.append((nx, ny))
    
    if (ex, ey) in visited:
        x, y = ex, ey
        while visited[(x, y)] is not None:
            if maze[y][x] == '#':
                maze[y][x] = '.'
            x, y = visited[(x, y)]
    else:
        x, y = sx, sy
        while x != ex or y != ey:
            if x < ex:
                x += 1
            elif x > ex:
                x -= 1
            elif y < ey:
                y += 1
            elif y > ey:
                y -= 1
            
            if 0 < x < width - 1 and 0 < y < height - 1:
                maze[y][x] = '.'
    
    return maze


def create_passages(maze, width, height):
    center_x = width // 2
    center_y = height // 2
    
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            nx, ny = center_x + dx, center_y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1:
                maze[ny][nx] = '.'
    
    return maze


def preview_maze(maze_path, preview_width=80):
    print("\nMaze preview:")
    print("-" * preview_width)
    
    with open(maze_path, 'r') as f:
        lines = f.readlines()
    
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
    parser.add_argument('--size', '-s', type=int, default=200, help='Maze size (max 200)')
    parser.add_argument('--threshold', '-t', type=int, default=128, help='Brightness threshold 0-255')
    parser.add_argument('--invert', '-i', action='store_true', help='Invert colors')
    parser.add_argument('--no-sharpen', action='store_true', help='Disable sharpening')
    parser.add_argument('--start', type=str, default=None, help='Start position x,y')
    parser.add_argument('--end', type=str, default=None, help='End position x,y')
    parser.add_argument('--preview', '-p', action='store_true', help='Show ASCII preview')
    parser.add_argument('--preview-width', type=int, default=80)
    
    args = parser.parse_args()
    
    args.size = min(200, max(10, args.size))
    
    if args.output is None:
        if '.' in args.input:
            base_name = '. '.join(args. input.split('.')[:-1])
        else:
            base_name = args. input
        args. output = base_name + '.warwickmaze'
    
    if not args.output. endswith('.warwickmaze'):
        if '.' in args.output:
            base_name = '.'.join(args.output. split('.')[:-1])
        else:
            base_name = args.output
        args.output = base_name + '. warwickmaze'
    
    start_pos = None
    end_pos = None
    
    if args.start:
        try:
            start_pos = tuple(map(int, args. start.split(',')))
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
            size=args.size,
            threshold=args.threshold,
            invert=args.invert,
            start_pos=start_pos,
            end_pos=end_pos,
            sharpen=not args.no_sharpen
        )
        
        if args.preview:
            preview_maze(args.output, args.preview_width)
        
        print("\nDone!")
        
    except FileNotFoundError:
        print(f"Error: Could not find: {args. input}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys. exit(1)


if __name__ == '__main__':
    main()