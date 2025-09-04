# Flask Executable Packager

This README file provides instructions on how to build an executable (.exe) file for the Flask application located in the `backend` directory. Follow the steps below to create the executable and run the application on other machines.

## Prerequisites

Before building the executable, ensure you have the following installed on your machine:

- Python (version 3.6 or higher)
- Pip (Python package installer)
- PyInstaller (or another packaging tool)

You can install PyInstaller using pip:

```
pip install pyinstaller
```

## Building the Executable

1. **Navigate to the Installer Directory**:
   Open a terminal and navigate to the `installer` directory where the `setup.spec` file is located.

   ```
   cd path/to/flask-exe-packager/installer
   ```

2. **Run PyInstaller**:
   Use PyInstaller to build the executable by running the following command:

   ```
   pyinstaller setup.spec
   ```

   This command will read the `setup.spec` file and create a `dist` directory containing the executable.

3. **Locate the Executable**:
   After the build process is complete, you can find the executable in the `dist` directory. The executable will have the same name as specified in the `setup.spec` file.

## Running the Executable

To run the executable, simply double-click on it or run it from the command line. Ensure that any required audio files are accessible to the application.

## Dependencies

The following Python libraries are required for the Flask application to function correctly:

- Flask
- librosa
- numpy
- joblib
- pydub

These dependencies are listed in the `backend/requirements.txt` file. You can install them using:

```
pip install -r path/to/flask-exe-packager/backend/requirements.txt
```

## Notes

- Ensure that the `scream_model.pkl` file is included in the build process as specified in the `setup.spec` file.
- If you encounter any issues during the build process, check the PyInstaller documentation for troubleshooting tips.

This README serves as a guide to help you successfully create and run the executable for the Flask application.