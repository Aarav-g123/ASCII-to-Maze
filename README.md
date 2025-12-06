# Image to WarwickMaze Converter

Convert any image into a playable maze for the Warwick CS118 Robot-Maze Environment.

## Installation

```bash
pip install Pillow
```

## Usage

Basic usage:
```bash
python image_to_maze.py photo.jpg
```

This creates `photo.warwickmaze` in the same directory. 

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--size` | `-s` | Maze size in pixels (default: 200, max: 200) |
| `--threshold` | `-t` | Brightness threshold 0-255 (default: 128) |
| `--invert` | `-i` | Invert colors (light becomes walls) |
| `--no-sharpen` | | Disable image sharpening |
| `--preview` | `-p` | Show ASCII preview in terminal |
| `--start` | | Manual start position as `x,y` |
| `--end` | | Manual end position as `x,y` |

### Examples

```bash
# Basic conversion
python image_to_maze.py logo.png

# With preview
python image_to_maze.py photo.jpg --preview

# Adjust threshold for dark images
python image_to_maze.py dark_image.png --threshold 80

# Invert for images with dark subject on light background
python image_to_maze.py silhouette.png --invert

# Smaller maze
python image_to_maze.py huge_image.jpg --size 100

# Manual start/end positions
python image_to_maze.py image.png --start 10,10 --end 190,190
```

## Tips for Best Results

| Image Type | Recommended Settings |
|------------|---------------------|
| Logo on inverted background | `--invert` |
| Dark photograph | `--threshold 80` |
| Light photograph | `--threshold 180` |
| High contrast art | Default settings |
| Line drawing | `--threshold 50` |

If your maze has no passages:
1. Try `--invert`
2. Try different `--threshold` values (50-200)
3. Use a higher contrast image

## Output Format

The generated `. warwickmaze` file should look like this:

```
Type: WarwickMaze
Version: 1.0
Width: 200
Height: 200
HeaderEnd
########################################
##>.... ................................ #
##. ####################################
##.####################################
##..... ................................#
######################################F#
########################################
```

### Symbols

| Symbol | Meaning |
|--------|---------|
| `#` | Wall |
| `.` | Passage |
| `>` | Start position (robot spawns here) |
| `F` | Finish/target position |

---

# The Warwick Robot-Maze Environment

## What Is It?

The Robot-Maze Environment is a Java application used in the University of Warwick CS118 course. It simulates a robot navigating through a maze, and students write Java controllers to guide the robot to the target. 

## Running the Environment

```bash
java -jar maze-environment.jar
```
## Loading Your Custom Maze

1. Generate a maze using this script:
   ```bash
   python image_to_maze.py my_image.jpg
   ```

2. Open the maze environment:
   ```bash
   java -jar maze-environment.jar
   ```

3. Click **Load Maze** and select `my_image.warwickmaze`

4. Load a controller and click **Start** to watch the robot solve it

## Writing Robot Controllers

Controllers are Java classes that implement the robot's behavior.  Here's a minimal example:

```java
import uk.ac.warwick.dcs.maze.logic.IRobot;

public class MyController {
    public void controlRobot(IRobot robot) {
        // Check surroundings
        if (robot.look(IRobot.AHEAD) != IRobot.WALL) {
            robot.face(IRobot.AHEAD);
        } else if (robot. look(IRobot.LEFT) != IRobot.WALL) {
            robot.face(IRobot. LEFT);
        } else if (robot. look(IRobot.RIGHT) != IRobot.WALL) {
            robot.face(IRobot.RIGHT);
        } else {
            robot.face(IRobot.BEHIND);
        }
    }
}
```

Compile with:
```bash
javac -classpath maze-environment.jar MyController.java
```

Then load `MyController.class` in the environment. 

## Robot API Reference

### Constants

**Directions (relative to robot):**
- `IRobot.AHEAD`, `IRobot.BEHIND`, `IRobot.LEFT`, `IRobot.RIGHT`

**Headings (absolute):**
- `IRobot.NORTH`, `IRobot.SOUTH`, `IRobot.EAST`, `IRobot.WEST`

**Square types:**
- `IRobot.WALL` - Wall or boundary
- `IRobot.PASSAGE` - Unvisited passage
- `IRobot.BEENBEFORE` - Previously visited passage

### Methods

| Method | Description |
|--------|-------------|
| `robot.look(direction)` | Returns what's in that direction (`WALL`, `PASSAGE`, or `BEENBEFORE`) |
| `robot.face(direction)` | Turn to face that direction |
| `robot.getHeading()` | Get current heading (`NORTH`, `SOUTH`, `EAST`, `WEST`) |
| `robot.setHeading(heading)` | Set absolute heading |
| `robot.getLocation()` | Returns `Point` with `. x` and `.y` coordinates |
| `robot.getTargetLocation()` | Returns target position as `Point` |
| `robot.getRuns()` | Number of previous runs on this maze |

### Example: Random Walker

```java
import uk.ac.warwick.dcs.maze.logic.IRobot;

public class RandomController {
    public void controlRobot(IRobot robot) {
        int[] directions = {IRobot.AHEAD, IRobot.LEFT, IRobot.RIGHT, IRobot.BEHIND};
        
        int direction;
        do {
            int rand = (int)(Math.random() * 4);
            direction = directions[rand];
        } while (robot.look(direction) == IRobot.WALL);
        
        robot.face(direction);
    }
}
```

### Example: Wall Follower

```java
import uk.ac.warwick.dcs.maze.logic. IRobot;

public class WallFollower {
    public void controlRobot(IRobot robot) {
        if (robot.look(IRobot.RIGHT) != IRobot.WALL) {
            robot.face(IRobot.RIGHT);
        } else if (robot. look(IRobot.AHEAD) != IRobot.WALL) {
            robot. face(IRobot.AHEAD);
        } else if (robot.look(IRobot.LEFT) != IRobot.WALL) {
            robot.face(IRobot. LEFT);
        } else {
            robot.face(IRobot.BEHIND);
        }
    }
}
```

## License

This converter script is provided for educational purposes. The Warwick Robot-Maze Environment is property of the University of Warwick Department of Computer Science. 