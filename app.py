import gradio as gr
"""
Gradio interface. This is the design for the front end of the code and how it connects to the rest of the project.
Contains:
    Inputs componenets: key dropdown, boxes for inputs, sort button
    Output display
    Sort button connection to sort_playlist() function
    app.launch 

"""

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

    # Record the split event — just the titles of each half
    steps.append({
        "type": "split",
        "left": [s['title'] for s in left_half],
        "right": [s['title'] for s in right_half]
    })

    #sort halves using recursion
    left_sorted = merge_sort(left_half, key, steps)
    right_sorted = merge_sort(right_half, key, steps)

    #combine sorted lists into one sorted list
    merged = merge(left_sorted, right_sorted, key)

    # Record the merge event — what two lists combined into what result
    steps.append({
        "type": "merge",
        "left": [s['title'] for s in left_sorted],
        "right": [s['title'] for s in right_sorted],
        "result": [s['title'] for s in merged]
    })

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

    # Find the longest entry in each column to use as padding
    title_width = max(len(song['title']) for song in songs)
    artist_width = max(len(song['artist']) for song in songs)

    # Ensure columns are at least as wide as their header
    title_width = max(title_width, len("Title"))
    artist_width = max(artist_width, len("Artist"))

    # Column headers with dynamic padding
    header = (f"{'#':<4} {'Title':<{title_width}} "
              f"{'Artist':<{artist_width}} {'Energy':>8} {'Duration':>10}") #header design/padding
    divider = "-" * (4 + title_width + artist_width + 22) #separates header from songs in playlist

    rows = []
    for i, song in enumerate(songs, start=1):
        row = (f"{i:<4} {song['title']:<{title_width}} "
               f"{song['artist']:<{artist_width}} " #row for each song + dynamic padding
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

    # Edge case: single song needs no sorting
    if len(songs) == 1:
        result = format_playlist(songs, key)
        steps_msg = "Only one song in the playlist — no sorting needed!"
        return result, steps_msg

    # Run merge sort, collecting steps along the way
    steps = []
    sorted_songs = merge_sort(songs, key, steps)

    # Format and return the sorted result
    result = format_playlist(sorted_songs, key)

    # Format each step as clean title only display
    steps_output = ""
    split_count = 0
    merge_count = 0

    for step in steps:
        if step["type"] == "split":
            split_count += 1
            steps_output += f"SPLIT {split_count}:\n"
            steps_output += f"  Left:  {step['left']}\n"
            steps_output += f"  Right: {step['right']}\n\n"
        elif step["type"] == "merge":
            merge_count += 1
            steps_output += f"MERGE {merge_count}:\n"
            steps_output += f"  {step['left']}\n"
            steps_output += f"  + {step['right']}\n"
            steps_output += f"  → {step['result']}\n\n"

    return result, steps_output



sample_playlist = """Blinding Lights, The Weeknd, 87, 200
Levitating, Dua Lipa, 72, 203
Stay, The Kid LAROI, 91, 141
good 4 u, Olivia Rodrigo, 65, 178
Peaches, Justin Bieber, 55, 198
Montero, Lil Nas X, 80, 137
drivers license, Olivia Rodrigo, 42, 242
Heat Waves, Glass Animals, 60, 238
As It Was, Harry Styles, 78, 167
Shivers, Ed Sheeran, 83, 207
Easy On Me, Adele, 30, 224
Industry Baby, Lil Nas X, 88, 212
Bad Habits, Ed Sheeran, 76, 231
Mood, 24kGoldn, 70, 141
Watermelon Sugar, Harry Styles, 68, 174"""

with gr.Blocks(title="Playlist Vibe Builder") as app: #container for playlist sorter

    gr.Markdown("# 🎵 Playlist Vibe Builder") #displays text, uses Markdown formatting
    gr.Markdown("Sort your playlist by **Energy Score** or **Duration** using the Merge Sort algorithm. The app will show you the final sorted playlist and every split and merge step the algorithm took to get there.")

    # ── INPUT SECTION ──────────────────────────────
    gr.Markdown("## 📋 Step 1 — Enter Your Playlist")
    gr.Markdown(
        "Enter one song per line using this exact format:\n\n"
        "```\n"
        "Title, Artist, Energy (0-100), Duration (seconds)\n"
        "```\n"
        "**Energy Score:** How energetic the song feels, from 0 (very calm) to 100 (very intense)\n\n"
        "**Duration:** Length of the song in seconds — for example, a 3 minute 20 second song = 200 seconds"
    )

    playlist_input = gr.Textbox(
        label="Your Playlist",
        lines=10,
        value=sample_playlist,
        info="A sample playlist is pre-loaded — feel free to edit it or replace it entirely"
    )

    # ── SORT KEY SECTION ───────────────────────────
    gr.Markdown("## 🔑 Step 2 — Choose How to Sort")
    gr.Markdown(
        "**Energy Score** — sorts from calmest to most energetic. Good for building up a vibe gradually.\n\n"
        "**Duration (seconds)** — sorts from shortest to longest song."
    )

    sort_key_dropdown = gr.Dropdown(
        choices=["Energy Score", "Duration (seconds)"],
        value="Energy Score",
        label="Sort By"
    )

    # ── SORT BUTTON ────────────────────────────────
    gr.Markdown("## ▶ Step 3 — Sort!")
    sort_button = gr.Button("Sort My Playlist!", variant="primary")

    # ── OUTPUT SECTION ─────────────────────────────
    gr.Markdown("## 📊 Results")
    gr.Markdown(
        "**Sorted Playlist** — your songs in sorted order from lowest to highest by your chosen key.\n\n"
        "**Step-by-Step Merge Process** — every split and merge the algorithm performed. "
        "SPLIT steps show the list being divided in half. MERGE steps show two sublists being combined in sorted order."
    )

    with gr.Row(): #display outputs side by side
        sorted_output = gr.Code(
            label="Sorted Playlist",
            lines=20,
            interactive=False,
            language=None
        )

        steps_output = gr.Code(
            label="Step-by-Step Merge Process",
            lines=20,
            interactive=False,
            language=None
        )

    sort_button.click(
        fn=sort_playlist,
        inputs=[playlist_input, sort_key_dropdown],
        outputs=[sorted_output, steps_output]
    )

app.launch()
