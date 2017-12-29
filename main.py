from mido import MidiFile, MetaMessage
import sys

DEFAULT_TEMPO = 0.5


def ticks2s(ticks, tempo, ticks_per_beat):
    """
        Converts ticks to seconds
    """
    return ticks/ticks_per_beat * tempo


def note2freq(x):
    """
        Convert a MIDI note into a frequency (given in Hz)
    """
    a = 440
    return (a/32) * (2 ** ((x-9)/12))


if __name__ == '__main__':

    # Import the MIDI file...
    mid = MidiFile(sys.argv[1])

    print("TYPE: " + str(mid.type))
    print("LENGTH: " + str(mid.length))
    print("TICKS PER BEAT: " + str(mid.ticks_per_beat))

    if mid.type == 3:
        print("Unsupported type.")
        exit()

    """
        First read all the notes in the MIDI file
    """

    tracksMerged = []
    notes = {}

    for i, track in enumerate(mid.tracks):
        tempo = DEFAULT_TEMPO
        totaltime = 0
        print("Track: " + str(i))

        for message in track:
            t = ticks2s(message.time, tempo, mid.ticks_per_beat)
            totaltime += t

            if isinstance(message, MetaMessage):  # Tempo change
                if message.type == "set_tempo":
                    tempo = message.tempo / 10**6
                elif message.type == "end_of_track":
                    pass
                else:
                    print("Unsupported metamessage: " + str(message))

            else:  # Note
                if message.type == "control_change" or \
                   message.type == "program_change":
                    pass

                elif message.type == "note_on" or message.type == "note_off":
                    if message.note not in notes:
                        notes[message.note] = 0
                    if message.type == "note_on" and message.velocity != 0:
                        notes[message.note] += 1
                        if(notes[message.note] == 1):
                            tracksMerged += \
                                [(totaltime, message.note, message.velocity)]

                    else:
                        notes[message.note] -= 1
                        if(notes[message.note] == 0):
                            tracksMerged += \
                                [(totaltime, message.note, message.velocity)]

                else:
                    print(message)

        print("totaltime: " + str(totaltime)+"s")

    """
        Now merge all the tracks alltogether
    """

    tracksMerged = sorted(tracksMerged, key=lambda x: x[0])
    music = []

    for i in range(len(tracksMerged)-1):
        a = tracksMerged[i][0]
        b = tracksMerged[i+1][0]
        t = round(b-a, 3)
        m = tracksMerged[i]
        music += [(t, round(note2freq(m[1])), m[2])]
    """
        Finally write it in CSV format in a file
    """

    he = ""
    for msg in music:
        he += str(msg[0])+","+str(msg[1])+","+str(msg[2])+";"
    f = open("/tmp/music.txt", "w")
    f.write(he)
    f.close()
