# sourcehold-maps [![Discord](https://img.shields.io/discord/1259903348077756527.svg?color=7389D8&label=%20&logo=discord&logoColor=ffffff)](https://discord.gg/SKJGEGgPTv) <!-- omit in toc -->
Reverse engineering the map file format of the 2D Stronghold Games.

### Project Goal <!-- omit in toc -->
The goal is to understand the [map file format](#map-file-format) of Stronghold, Stronghold Crusader and Stronghold Crusader Extreme and to be able to [manipulate](#tools) it.

## 🚀 Unified Windows Installer

**NEW!** We now provide a unified Windows installer that automatically installs all dependencies and provides both GUI and CLI interfaces for map conversion and AIV file processing.

### Quick Start
1. Download the latest installer from [Releases](https://github.com/sourcehold/sourcehold-maps/releases)
2. Run `SourceholdMapsConverter-Setup.exe`
3. Follow the installation wizard
4. Use the desktop shortcuts to launch the converter

### Features
- ✅ **Automatic dependency installation** (Python 3.11, Visual C++ Redistributable)
- ✅ **GUI interface** for easy file selection and conversion
- ✅ **CLI interface** for command-line usage
- ✅ **Map file support** (pack/unpack .map, .sav, .msv files)
- ✅ **AIV conversion** (.AIV to .AIVJSON format)
- ✅ **Desktop shortcuts** for quick access
- ✅ **Silent installation** option available

### Build Status
[![Build Installer](https://github.com/sourcehold/sourcehold-maps/workflows/Build%20Installer/badge.svg)](https://github.com/sourcehold/sourcehold-maps/actions?query=workflow%3A%22Build+Installer%22)

# Table of Contents <!-- omit in toc -->

- [🚀 Unified Windows Installer](#-unified-windows-installer)
- [Map File Format](#map-file-format)
- [Tools](#tools)
  - [Online Map Unpacking, Repacking and Exploring](#online-map-unpacking-repacking-and-exploring)
  - [Python Library](#python-library)
    - [Unpacking (CL)](#unpacking-cl)
    - [(Re-) Packing (CL)](#re--packing-cl)
    - [Generate Images of Map Sections (CL)](#generate-images-of-map-sections-cl)
    - [Map Preview Image (CL)](#map-preview-image-cl)
    - [Modify Map Properties](#modify-map-properties)
    - [Installation](#installation)
  - [Windows Installer](#windows-installer)
    - [Installation](#installation-1)
    - [Usage](#usage)
    - [Features](#features)
    - [Troubleshooting](#troubleshooting)
- [Development](#development)
  - [Building the Installer](#building-the-installer)
  - [GitHub Actions](#github-actions)
- [Contribute](#contribute)

# Map File Format
The current knowledge of the map file format (`*.map`, `*.sav` and `*.msv`) is documented in a human-readable form in the [wiki](https://github.com/sourcehold/sourcehold-maps/wiki) and in a machine-readable form in [here](/structure).

# Tools

## Online Map Unpacking, Repacking and Exploring
If you don't want to install the python library and jump directly into action, there is an [online tool](https://sourcehold.github.io/sourcehold-maps/) to unpack, repack and visualize map sections.

## Python Library
The python library contains multiple useful tools to interact with map files. The most important tools are directly accessible using the command line (CL), but most of the stuff is access

### Unpacking (CL)
Unpack map files to a folder:
```console
python -m sourcehold --in "mymap.map" "mymap2.map" "mysav.sav" --unpack
```
Unpack single sections:
```console
python -m sourcehold --in "mymap.map" "mysave.sav" --unpack --what 1107
```

### (Re-) Packing (CL)
Repack map folder to a file:
```console
python -m sourcehold --in "mymap/" "mymap2/" "mysav/" --pack
```

### Generate Images of Map Sections (CL)
```console
python examples/map_section_imaging.py "mymap.map" "mymap_images"
```

### Map Preview Image (CL)
Extract an image:
```console
python examples/map_preview_image.py extract "mymap.map" "mymap.png"
```

Substitute an image:
```console
python examples/map_preview_image.py replace "mymap.map" --replacement "mymap.png" "mymap_modified.map"
```

### Modify Map Properties
Disable buildings:
```python
from sourcehold import load_map, expand_var_path, save_map
# You can configure your installation folder (where shcmap points to) in /config.json
map = load_map(expand_var_path('shcmap~/mymap.map'))
map.directory["building_availability"].granary = False
save_map(map, expand_var_path('shcusermap~/mymap_modified.map'))
```

Set starting popularity and goods:
```python
from sourcehold import load_map, expand_var_path, save_map
map = load_map(expand_var_path('shcmap~/mymap.map'))
map.directory['STARTING_GOODS'].wood = 0
save_map(map, expand_var_path('shcusermap~/mymap_modified.map'))
```

### Installation
Find the right wheel file for your OS and (python) architecture [here](https://github.com/sourcehold/sourcehold-maps/actions?query=workflow%3A%22Python+package%22) (download the artifacts of the latest successful build).
Then install using pip:
```console
python -m pip install sourcehold.whl
```

## Windows Installer

### Installation
1. **Download** the latest installer from [Releases](https://github.com/sourcehold/sourcehold-maps/releases)
2. **Run** `SourceholdMapsConverter-Setup.exe` as administrator
3. **Follow** the installation wizard
4. **Use** desktop shortcuts to launch the converter

### Usage

#### GUI Interface
- Double-click the desktop shortcut **"Sourcehold Maps Converter"**
- Select input files (map files or AIV files)
- Choose operation (Unpack, Pack, or Convert AIV)
- Click **"Start Conversion"**

#### CLI Interface
```bash
# Open Command Prompt and navigate to installation directory
cd "C:\Program Files\Sourcehold Maps Converter"

# Unpack map files
sourcehold-converter-cli.exe --unpack "mymap.map"

# Pack map folders
sourcehold-converter-cli.exe --pack "mymap/"

# Convert AIV files
sourcehold-converter-cli.exe --convert-aiv "myai.aiv"
```

### Features
- **Automatic Dependencies**: Installs Python 3.11 and Visual C++ Redistributable
- **GUI Interface**: User-friendly interface for file selection and conversion
- **CLI Interface**: Command-line interface for automation
- **Map Support**: Pack/unpack .map, .sav, .msv files
- **AIV Conversion**: Convert .AIV files to .AIVJSON format
- **Desktop Shortcuts**: Quick access to both GUI and CLI
- **Silent Installation**: Available for automated deployment

### Troubleshooting
- **Installation fails**: Run as administrator
- **GUI doesn't start**: Check if Python is properly installed
- **Missing dependencies**: Re-run the installer
- **Permission errors**: Ensure you have admin rights

## Development

### Building the Installer
```bash
# Clone the repository
git clone https://github.com/sourcehold/sourcehold-maps.git
cd sourcehold-maps

# Install dependencies
pip install -r requirements.txt

# Download system dependencies
python download_dependencies.py

# Build executables
python build_exe.py

# Build installer
python build_installer.py
```

### GitHub Actions
The installer is automatically built using GitHub Actions:

- **Automatic builds** on push to main/master
- **Manual builds** via workflow_dispatch
- **Release builds** when tags are created
- **Artifacts** available for download

See [GITHUB_ACTIONS_README.md](GITHUB_ACTIONS_README.md) for detailed information.

# Contribute
There are multiple ways to contribute to this project, see [Contributing.md](/CONTRIBUTING.md) for more information.
