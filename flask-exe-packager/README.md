# Flask Executable Packager

This project is designed to package a Flask application into a standalone executable (.exe) file that can be easily distributed and run on other machines without requiring a Python installation.

## Project Structure

The project consists of the following main components:

- **backend/**: Contains the main Flask application code and model.
  - **app.py**: The main application file that defines the API endpoints and handles audio processing.
  - **requirements.txt**: Lists all the necessary Python dependencies for the application.
  - **model/**: Directory containing the pre-trained machine learning model.
    - **scream_model.pkl**: The serialized model used for predictions.

- **build/**: Contains documentation related to the build process.
  - **README.md**: Instructions on how to create the executable and any necessary configurations.

- **installer/**: Contains the packaging configuration.
  - **setup.spec**: Configuration file for the packaging tool (e.g., PyInstaller) that specifies how to build the executable.

## Installation Instructions

1. Clone the repository to your local machine.
2. Navigate to the `backend` directory and install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. To create the executable, navigate to the `installer` directory and run the packaging tool with the provided `setup.spec` file:
   ```
   pyinstaller setup.spec
   ```

## Usage

Once the executable is created, you can run it on any compatible machine. The application will start a Flask server that listens for audio file uploads and returns predictions on whether the audio contains a scream.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.