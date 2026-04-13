#!/usr/bin/env swift
import Speech
import AVFoundation
import AppKit

// Request authorization
SFSpeechRecognizer.requestAuthorization { status in
    guard status == .authorized else {
        print("ERROR: Speech recognition not authorized")
        print("Please enable in System Preferences > Privacy & Security > Speech Recognition")
        exit(1)
    }
    
    guard let recognizer = SFSpeechRecognizer() else {
        print("ERROR: No speech recognizer available")
        exit(1)
    }
    
    guard recognizer.isAvailable else {
        print("ERROR: Speech recognizer not available")
        exit(1)
    }
    
    let request = SFSpeechAudioBufferRecognitionRequest()
    request.shouldReportPartialResults = false
    
    let audioEngine = AVAudioEngine()
    let inputNode = audioEngine.inputNode
    let recordingFormat = inputNode.outputFormat(forBus: 0)
    
    inputNode.installTap(onBus: 0, bufferSize: 4096, format: recordingFormat) { buffer, _ in
        request.append(buffer)
    }
    
    do {
        try audioEngine.start()
    } catch {
        print("ERROR: \(error.localizedDescription)")
        exit(1)
    }
    
    print("LISTENING...")
    fflush(stdout)
    
    var finalText = ""
    let task = recognizer.recognitionTask(with: request) { result, error in
        if let result = result {
            finalText = result.bestTranscription.formattedString
            if result.isFinal {
                audioEngine.stop()
                inputNode.removeTap(onBus: 0)
                request.endAudio()
                print("TEXT:\(finalText)")
                exit(0)
            }
        }
        if error != nil {
            audioEngine.stop()
            inputNode.removeTap(onBus: 0)
            request.endAudio()
            if !finalText.isEmpty {
                print("TEXT:\(finalText)")
            }
            exit(0)
        }
    }
    
    // Listen for 8 seconds max
    DispatchQueue.main.asyncAfter(deadline: .now() + 8) {
        audioEngine.stop()
        inputNode.removeTap(onBus: 0)
        request.endAudio()
        task.cancel()
        if !finalText.isEmpty {
            print("TEXT:\(finalText)")
        }
        exit(0)
    }
    
    RunLoop.main.run()
}
RunLoop.main.run()
