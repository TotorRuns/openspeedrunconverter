# OpenSpeedrunConverter

OpenSpeedrunConverter is a desktop application that converts LiveSplit Split files (`.lss`) into a custom JSON format, suitable for use with the OpenSpeedrun platform. It also extracts and saves associated icons.

## Features

*   Converts LiveSplit `.lss` files to a structured JSON format.
*   Extracts game name, category, individual split names, and associated icons.
*   Automatically saves the converted JSON file and extracted icons to the user's operating system-specific configuration directory (`~/.config/openspeedrun` on Linux, `~/Library/Application Support/openspeedrun` on macOS, and `%LOCALAPPDATA%\openspeedrun` on Windows).

## Usage

1.  **Run the application:**
    If you have a compiled executable (from the [Releases](#releases) section), simply run it.
    If running from source, navigate to the project directory in your terminal and execute:
    ```bash
    python main.py
    ```
2.  **Select a LiveSplit file:** Click the "Select File" button and choose your `.lss` file.
3.  **Conversion and Saving:** The application will automatically convert the file and save the resulting JSON and any extracted icons to the appropriate user configuration directory. A message will appear in the application's output area indicating the success of the conversion and the save location.

## Building from Source

To build or run this project from its source code, you'll need Python 3 and PyQt5.

### Prerequisites

*   Python 3.x
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:TotorRuns/openspeedrunconverter.git
    cd openspeedrunconverter
    ```
2.  **Install dependencies:**
    ```bash
    pip install PyQt5 pyinstaller
    ```

### Running from Source

```bash
python main.py
```

### Compiling Executables

This project uses [PyInstaller](https://pyinstaller.org/) to create standalone executables for various platforms.

To compile manually:

```bash
pyinstaller --onefile --windowed main.py
```

The executable will be found in the `dist/` directory.

## Continuous Integration / Continuous Deployment (CI/CD)

This project utilizes [GitHub Actions](.github/workflows/build.yml) to automate the build process for Linux, Windows, and macOS whenever changes are pushed to the `main` or `release` branches. Compiled executables are available as artifacts in the GitHub Actions workflow runs.

## Releases

Compiled binaries for different operating systems will be available in the [Releases](https://github.com/TotorRuns/openspeedrunconverter/releases) section of this repository (once you create them from your GitHub Actions artifacts).

## License

[TODO: Add your license information here, e.g., MIT License]