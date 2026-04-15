def merge(left, right, key):
    result = [] #sorted playlist
    i = 0 #left pointer
    j = 0 #right pointer

    while i < len(left) and j < len(right): #both lists have unsorted songs
        if left[i][key] <= right[j][key]: #compare songs by chosen key (maintains list stability)
            #lower song is appended & respective pointer incrememted
            result.append(left[i])
            i += 1 
        else: 
            result.append(right[j]) 
            j += 1

    #append remaining songs
    result.extend(left[i:])
    result.extend(right[j:]) 

    return result


def merge_sort(songs, key, steps):
    #Check base case
    if len(songs) <= 1:
        return songs

    #splitting list in half
    mid = len(songs) // 2
    left_half = songs[:mid]
    right_half = songs[mid:]

    #sort halves using recusion
    left_sorted = merge_sort(left_half, key, steps) 
    right_sorted = merge_sort(right_half, key, steps)

    #combine sorted lists into one sorted list
    merged = merge(left_sorted, right_sorted, key)
    steps.append(merged[:]) #to be used for Merge Sort visual

    return merged


def parse_playlist(raw_text):
    """
    User input -> song info for dictionary

    Required format: Title, Artist, EnergyScore, Duration
    Only one song per line
    """

    songs = []  #playlist dictionary

    # Check for empty input before doing anything else
    if raw_text.strip() == "":
        raise ValueError("Your playlist is empty. Please add at least one song.")

    lines = raw_text.strip().split("\n")

    for line_number, line in enumerate(lines, start=1):
        line = line.strip() #removes whitespace
        if line == "":
            continue #skips extra lines

        parts = line.split(",") #split each line into its information

        # Check each line has exactly 4 fields
        if len(parts) != 4:
            raise ValueError(
                f"Line {line_number} has {len(parts)} field(s) but 4 are needed.\n"
                f"Expected format: Title, Artist, Energy, Duration\n"
                f"You entered: '{line}'"
            )

        #extracts each field and strips it
        title = parts[0].strip()
        artist = parts[1].strip()

        # Check energy a valid int
        try:
            energy = int(parts[2].strip())
        except ValueError:
            raise ValueError(
                f"Line {line_number}: Energy must be a whole number.\n"
                f"You entered: '{parts[2].strip()}'"
            )

        # Check duration is a valid int
        try:
            duration = int(parts[3].strip())
        except ValueError:
            raise ValueError(
                f"Line {line_number}: Duration must be a whole number.\n"
                f"You entered: '{parts[3].strip()}'"
            )

        # Check energy is within valid range
        if not (0 <= energy <= 100):
            raise ValueError(
                f"Line {line_number}: Energy must be between 0 and 100.\n"
                f"You entered: {energy}"
            )

        # Check duration is positive
        if duration <= 0:
            raise ValueError(
                f"Line {line_number}: Duration must be a positive number.\n"
                f"You entered: {duration}"
            )

        songs.append({
            "title": title,
            "artist": artist,
            "energy": energy,
            "duration": duration
        })

    return songs


def format_playlist(songs, key):
    # Dictionary -> formatted and readable table of songs and their corresponding info

    # Column headers
    header = f"{'#':<4} {'Title':<25} {'Artist':<20} {'Energy':>8} {'Duration':>10}" #header design/padding
    divider = "-" * 70 #separates header from songs in playlist
    
    rows = []
    for i, song in enumerate(songs, start=1): 
        row = (f"{i:<4} {song['title']:<25} {song['artist']:<20}" #row for each song + padding
               f"{song['energy']:>8} {song['duration']:>10}s") #s at end for duration of songs (60 -> 60s)
        rows.append(row)
    
    return "\n".join([header, divider] + rows) #header, divider, row1, row2,...


def sort_playlist(raw_playlist, sort_key):
    # Map the dropdown label to the actual dictionary key
    key_map = {
        "Energy Score": "energy",
        "Duration (seconds)": "duration"
    }
    key = key_map[sort_key] #users choice

    # Attempt to parse the input, display error message if something is wrong
    try:
        songs = parse_playlist(raw_playlist)
    except ValueError as e:
        return f"❌ Input Error:\n{str(e)}", ""

    # Run merge sort, collecting steps along the way
    steps = []
    sorted_songs = merge_sort(songs, key, steps)

    # Format and return the sorted result
    result = format_playlist(sorted_songs, key)

        # Format each step and return alongside the sorted result
    steps_output = ""
    for i, snapshot in enumerate(steps, start=1):
        steps_output += f"Step {i}:\n"
        steps_output += format_playlist(snapshot, key)
        steps_output += "\n\n"

    return result, steps_output



import gradio as gr 
"""
Gradio interface. This is the design for the front end of the code and how it connects to the rest of the project.
Contains:
    Inputs componenets: key dropdown, boxes for inputs, sort button
    Output display
    Sort button connection to sort_playlist() function
    app.launch 

"""


sample_playlist = """Blinding Lights, The Weeknd, 87, 200
Levitating, Dua Lipa, 72, 203
Stay, The Kid LAROI, 91, 141
good 4 u, Olivia Rodrigo, 65, 178
Peaches, Justin Bieber, 55, 198"""

with gr.Blocks(title="Playlist Vibe Builder") as app: #container for playlist sorter
    
    gr.Markdown("# 🎵 Playlist Vibe Builder") #displays text, uses Markdown formatting
    gr.Markdown("Enter your playlist, choose a sorting key, and watch Merge Sort order your songs!")
    
    playlist_input = gr.Textbox( #
        label="Enter Your Playlist",
        lines=10,
        value=sample_playlist,
        info="One song per line. Format: Title, Artist, Energy (0-100), Duration (seconds)"
    )
    
    sort_key_dropdown = gr.Dropdown(
        choices=["Energy Score", "Duration (seconds)"],
        value="Energy Score",
        label="Sort By"
    )
    
    sort_button = gr.Button("Sort My Playlist!")
    
    sorted_output = gr.Textbox(
        label="Sorted Playlist",
        lines=10,
        interactive=False
    )
    steps_output = gr.Textbox(
        label="Step-by-Step Merge Process",
        lines=20,
        interactive=False
    )

    sort_button.click(
        fn=sort_playlist,
        inputs=[playlist_input, sort_key_dropdown],
        outputs=[sorted_output, steps_output]
    )
    
app.launch()