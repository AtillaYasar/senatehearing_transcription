# note: time_offset in parse_timestamp, and the speaker_names dict are done manually.

import json
path = 'sam_senate.srt'
with open(path, 'r') as f:
    transcript = f.read()

def parse_timestamp(string):
    # takes a string like "00:02:17" and returns a tuple like (0, 2, 17)
    assert isinstance(string, str)
    hours, minutes, seconds_ms = string.split(':')
    seconds, milliseconds = seconds_ms.split(',')
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    milliseconds = int(milliseconds)
    seconds = seconds + milliseconds/1000

    time_offset = (0, 2, 39)
    hours += time_offset[0]
    minutes += time_offset[1]
    seconds += time_offset[2]

    if seconds >= 60:
        minutes += 1
        seconds -= 60
    if minutes >= 60:
        hours += 1
        minutes -= 60

    return (hours, minutes, seconds)

extracted = []
lines = transcript.split('\n')
for n in range(0, len(lines), 4):
    first_line = lines[n]
    second_line = lines[n+1]
    third_line = lines[n+2]
    fourth_line = lines[n+3]

    timestamp_range = second_line
    timestamp_start, _, timestamp_end = timestamp_range.partition(' --> ')
    timestamp_start = parse_timestamp(timestamp_start)
    timestamp_end = parse_timestamp(timestamp_end)

    prespeaker, _, text = third_line.partition(': ')
    speaker = prespeaker[1:-1]

    extracted.append({
        'timestamp_range': timestamp_range,
        'timestamp_start': timestamp_start,
        'timestamp_end': timestamp_end,
        'speaker': speaker,
        'text': text
    })

with open('from_srt_first.json', 'w') as f:
    json.dump(extracted, f, indent=4)

# filling these manually
speaker_names = {
    0: 'Ms. Black',
    1: 'Mr. Kennedy',
    2: 'Ms. Christina Montgomery',
    3: 'Ms. Klobuchar',
    4: 'Mr. Graham/Mr. Altman',
    5: 'Mr. Kennedy',
    6: 'Mr. Booker',
    7: 'Mr. Coons',
    8: 'Ms. Christina Montgomery',
    9: 'Mr. Blumenthal',
    10: 'Mr. Padilla',
    11: 'Mr. Osoff',
    12: 'Mr. Welch',
    13: 'Mr. Padilla',
    14: 'Mr. Hawley',
    15: 'Mr. Altman',
}
def mapper(n):
    if n < 10:
        string = 'SPEAKER_0' + str(n)
    else:
        string = 'SPEAKER_' + str(n)
    return string
speaker_names = {mapper(k): v for k, v in speaker_names.items()}


# combine each speaker's lines into one
cleaned = []
current_speaker = None
current_timestamp_start = (0, 0, 0)
current_lines = []
for item in extracted:
    timestamp_start = item['timestamp_start']
    timestamp_end = item['timestamp_end']
    speaker = item['speaker']
    text = item['text']
    
    if speaker in speaker_names:
        speaker = speaker_names[speaker]

    if speaker == current_speaker:
        current_lines.append(text)
    else:
        # speaker changed
        # write current lines to cleaned
        cleaned.append({
            'speaker': current_speaker,
            'timestamp_range': (current_timestamp_start, timestamp_end),
            'text': '\n'.join(current_lines),
        })

        # reset current lines
        current_lines = [text]
        # reset current speaker
        current_speaker = speaker
        # reset current timestamp start
        current_timestamp_start = timestamp_start

# write last item
cleaned.append({
    'speaker': current_speaker,
    'timestamp_range': (current_timestamp_start, timestamp_end),
    'text': '\n'.join(current_lines),
})

with open('from_srt_cleaned.json', 'w') as f:
    json.dump(cleaned, f, indent=4)

# now create a nice human-readable text.
tuple_to_readable = lambda t: f'{t[0]:02}:{t[1]:02}:{int(t[2]):02}'
lines = []
for item in cleaned:
    speaker = item['speaker']
    timestamp_range = item['timestamp_range']
    text = item['text']

    timestamp_range = tuple_to_readable(timestamp_range[0]) + ' --> ' + tuple_to_readable(timestamp_range[1])

    lines.append(timestamp_range)
    lines.append(speaker)
    lines.append(text)
    lines.append('')

with open('from_srt_cleaned.txt', 'w') as f:
    f.write('\n'.join(lines))

