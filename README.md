# Wordle Game with Pygame

A Python implementation of the popular Wordle game using Pygame. This game features smooth animations, visual feedback, and an intuitive interface.

## Features

- **Classic Wordle Gameplay**: Guess a 5-letter word in 6 attempts
- **Visual Feedback**: Color-coded tiles (Green = correct position, Yellow = correct letter wrong position, Gray = not in word)
- **Smooth Animations**: Flip animations, pop effects, and shake animations for invalid inputs
- **Modern UI**: Clean interface with custom fonts and rounded corners
- **Real-time Validation**: Checks if entered words are in the word list

## Requirements

- Python 3.7 or higher
- Pygame library
- Custom fonts (Poppins and Helvetica)

## Installation

1. **Clone or download the project files**
   ```bash
   git clone [<repository-url>](https://github.com/shelterin2006/Wordle)
   cd wordle-game
   ```

2. **Install Python dependencies**
   ```bash
   pip install pygame
   ```

3. **Download required fonts**
   - Create a `font` folder in your project directory
   - Download and place the following font files in the `font` folder:
     - `Poppins-Regular.ttf`
     - `Helvetica.ttf`

4. **Download word list**
   - Download `wordle.json` file containing the list of valid words
   - Place it in the same directory as `main.py`

## File Structure

```
wordle-game/
├── main.py              # Main game file
├── wordle.json          # Word list database
├── font/                # Font files directory
│   ├── Poppins-Regular.ttf
│   └── Helvetica.ttf
└── README.md            # This file
```

## How to Run

1. **Navigate to the project directory**
   ```bash
   cd wordle-game
   ```

2. **Run the game**
   ```bash
   python main.py
   ```

## How to Play

1. **Objective**: Guess the 5-letter word in 6 attempts
2. **Input**: Type letters using your keyboard
3. **Submit**: Press Enter to submit your guess
4. **Feedback**: 
   - 🟩 Green: Correct letter in correct position
   - 🟨 Yellow: Correct letter in wrong position  
   - ⬜ Gray: Letter not in the word
5. **Navigation**: Use Backspace to delete letters
6. **Restart**: Press any key after game over to play again

## Game Controls

- **Letter Keys (A-Z)**: Enter letters
- **Enter**: Submit your guess
- **Backspace**: Delete the last letter
- **Any Key**: Restart game after completion

## Technical Details

### Architecture
- **Main Loop**: Async-based game loop for smooth performance
- **Tile System**: Individual tile objects with animation states
- **Animation Engine**: Custom animation system for flips, pops, and shakes
- **Event Handling**: Pygame event system for input processing

### Key Components
- `Tile` class: Manages individual letter squares with animations
- `get_feedback()`: Calculates color feedback for guesses
- `main()`: Core game logic and rendering loop
- Animation system: Handles flip, pop, and shake effects

### Performance
- 60 FPS target frame rate
- Delta time-based animations
- Efficient surface rendering with transformations

## Customization

### Colors
You can modify the color scheme by changing the RGB values:
```python
GREEN = (106, 170, 100)      # Correct position
YELLOW = (201, 180, 88)      # Correct letter, wrong position  
DARK_GRAY = (120, 124, 126)  # Not in word
```

### Game Settings
Adjust game parameters:
```python
WORD_LENGTH = 5              # Length of words
MAX_GUESSES = 6              # Number of attempts
SQUARE_SIZE = 80             # Size of letter squares
```

### Animation Speed
Modify animation parameters in the `Tile` class:
```python
"speed": 700,                # Flip animation speed
"speed": 0.1,                # Pop animation speed
"speed": 50                  # Shake animation speed
```

## Troubleshooting

### Common Issues

1. **Font not found error**
   - Ensure font files are in the `font/` directory
   - Check file names match exactly: `Poppins-Regular.ttf`, `Helvetica.ttf`

2. **Word list not found**
   - Make sure `wordle.json` is in the same directory as `main.py`
   - Verify the JSON file contains a valid word list

3. **Pygame not installed**
   - Run: `pip install pygame`
   - For Python 3.10+: `pip install pygame --upgrade`

4. **Performance issues**
   - Close other applications
   - Check if your system meets the requirements

## Dependencies

- `pygame`: Game development library
- `asyncio`: Asynchronous programming support
- `math`: Mathematical functions for animations
- `random`: Random word selection
- `json`: Word list parsing

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## Acknowledgments

- Inspired by the original Wordle game
- Built with Pygame framework
- Uses Poppins and Helvetica fonts
