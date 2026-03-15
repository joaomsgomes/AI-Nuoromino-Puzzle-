# AI Nuoromino Puzzle Solver 🧩

## Overview

The **AI Nuoromino Puzzle Solver** is an artificial intelligence system designed to solve Nuoromino puzzles using search algorithms and constraint-based problem solving.

Nuoromino puzzles require placing geometric pieces on a grid while respecting placement rules and spatial constraints. This project models the puzzle as a search problem and applies algorithmic techniques to efficiently explore the solution space.

The system demonstrates core concepts in **artificial intelligence, state space search, constraint satisfaction, and algorithm optimization**.

---

## Features

* Puzzle representation using grid-based state modeling
* Automated puzzle solving using search algorithms
* Constraint validation for piece placement
* Exploration of the state space to find valid solutions
* Efficient pruning of invalid states

---

## Tech Stack

**Language**

* Python

**Concepts**

* Artificial Intelligence
* State Space Search
* Constraint Satisfaction Problems (CSP)
* Algorithm Optimization
* Problem Modeling

---

## Project Structure

```id="p0xxss"
AI-Nuoromino-Puzzle
│
├── search.py        # Search algorithm implementation
├── problem.py       # Puzzle modeling and constraints
├── utils.py         # Utility functions
├── puzzles/         # Example puzzle instances
└── README.md
```

---

## Installation

### Requirements

* Python 3.9+

No additional external dependencies are required.

---

## Running the Solver

To run the puzzle solver:

```bash id="4xqv1l"
python search.py < puzzle_instance.txt
```

Example:

```bash id="n8dz5q"
python search.py < puzzles/example.txt
```

The program will process the puzzle instance and output the solved grid configuration if a valid solution is found.

---

## How It Works

The solver approaches the Nuoromino puzzle as a **search problem**:

1. The puzzle is represented as a **state space**
2. Each state represents a partial or complete board configuration
3. The solver explores possible placements of pieces
4. Invalid states are pruned using constraint validation
5. The algorithm searches until a valid solution is found

This approach allows the system to systematically explore the solution space while avoiding unnecessary computations.

---

## Project Status 🚧

This project is currently functional but open for improvements.

### Current Capabilities

* Puzzle modeling
* State-space search solver
* Constraint validation
* Execution via command-line

### Planned Improvements

* Implement additional search strategies (A*, heuristic search)
* Improve solver performance and pruning techniques
* Add visualization of puzzle states
* Support additional puzzle sizes and configurations
* Implement benchmarking for solver performance
* Add interactive interface for puzzle input

---

## Future Ideas

Possible extensions for the project include:

* Graphical visualization of puzzle solving steps
* Interactive puzzle editor
* Heuristic-based search improvements
* Integration with other puzzle-solving frameworks
* Performance comparison between different search strategies

---

## Contributing

Contributions are welcome!

If you'd like to improve the solver or experiment with new algorithms:

1. Fork the repository
2. Create a new branch

```bash id="f7q0pl"
git checkout -b feature/improvement
```

3. Commit your changes

```bash id="hy8q7f"
git commit -m "Improve search algorithm"
```

4. Push your branch

```bash id="mny0n8"
git push origin feature/improvement
```

5. Open a Pull Request

Bug reports, optimizations, and new search strategies are highly appreciated.

---

## License

This project is intended for experimentation and learning purposes within artificial intelligence and algorithm development.
