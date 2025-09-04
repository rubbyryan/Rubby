import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'package:permission_handler/permission_handler.dart';

void main() {
  runApp(const ScreamDetectionApp());
}

class ScreamDetectionApp extends StatelessWidget {
  const ScreamDetectionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Scream Detection',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const ScreamDetectionHomePage(),
    );
  }
}

class ScreamDetectionHomePage extends StatefulWidget {
  const ScreamDetectionHomePage({super.key});

  @override
  State<ScreamDetectionHomePage> createState() => _ScreamDetectionHomePageState();
}

class _ScreamDetectionHomePageState extends State<ScreamDetectionHomePage> {
  late final Record _recorder = Record(); // Use late initialization
  bool _isRecording = false;
  String _result = '';
  final String _backendUrl = 'http://192.168.1.148:5000/predict'; // <-- Set your backend IP here

  Future<void> _startRecording() async {
    if (await Permission.microphone.request().isGranted) {
      await _recorder.start(
        encoder: AudioEncoder.wav,
        bitRate: 128000,
        samplingRate: 16000,
      );
      setState(() => _isRecording = true);
    } else {
      setState(() => _result = 'Microphone permission denied');
    }
  }

  Future<void> _stopAndSend() async {
    final path = await _recorder.stop();
    setState(() => _isRecording = false);

    if (path != null) {
      setState(() => _result = 'Processing...');
      try {
        var request = http.MultipartRequest('POST', Uri.parse(_backendUrl));
        request.files.add(await http.MultipartFile.fromPath('file', path));
        var response = await request.send();

        if (response.statusCode == 200) {
          final respStr = await response.stream.bytesToString();
          setState(() => _result = respStr);
        } else {
          setState(() => _result = 'Error: ${response.statusCode}');
        }
      } catch (e) {
        setState(() => _result = 'Error: $e');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scream Detection')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton.icon(
                icon: Icon(_isRecording ? Icons.stop : Icons.mic),
                label: Text(_isRecording ? 'Stop & Send' : 'Start Recording'),
                onPressed: _isRecording ? _stopAndSend : _startRecording,
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(200, 50),
                  textStyle: const TextStyle(fontSize: 18),
                ),
              ),
              const SizedBox(height: 32),
              Text(
                _result.isNotEmpty ? _result : 'Awaiting input...',
                style: const TextStyle(fontSize: 16),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}