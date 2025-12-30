// SuperDirt Startup for Zeph's Studio
// Model D on MIDI Channel 11

(
s.reboot { // reboot server
    s.options.numBuffers = 1024 * 256; // increase buffer count
    s.options.memSize = 8192 * 32; // increase memory
    s.options.numWireBufs = 2048; // increase wire buffers
    s.options.maxNodes = 1024 * 32; // increase max nodes
    s.options.numOutputBusChannels = 2;
    s.options.numInputBusChannels = 2;

    s.waitForBoot {
        ~dirt = SuperDirt(2, s); // two output channels

        // Load default samples
        ~dirt.loadSoundFiles;

        s.sync; // wait for samples to load

        // Start listening for Tidal messages
        ~dirt.start(57120, 0 ! 12);

        // Initialize MIDI
        MIDIClient.init;

        // Find Model D
        ~midiOut = MIDIOut.newByName("MODEL D", "MODEL D");

        // Set latency to match audio
        ~midiOut.latency = s.latency;

        // Make it available globally
        ~dirt.soundLibrary.addMIDI(\modeld, ~midiOut);

        // Info
        "\n\n".postln;
        "==============================================".postln;
        "SuperDirt ready!".postln;
        "Model D MIDI configured on: \\modeld".postln;
        "Use in Tidal: d1 $ n \"0 2 4\" # s \"modeld\" # midichan 10".postln;
        "(midichan 10 = MIDI channel 11)".postln;
        "==============================================".postln;
        "\n".postln;
    };
};
)
