from re import split
import subprocess, os, yaml, json

DEFAULT_FILTER_CONFIG_FILE = 'filters.yml'
FFMPEG_BIN : list = "ffmpeg -v error -y".split()

class Utils:

    @staticmethod
    def ensure_list(variable):
        if not isinstance(variable, list):
            return [variable]
        return variable

    @staticmethod
    def json_parsor(file):
        with open(file, 'r') as yaml_in:
            yaml_object = yaml.safe_load(yaml_in)
            _g = json.dumps(yaml_object)
            return json.loads(_g)

class MediaOperation:

    def __init__(self):
        self.file: str = DEFAULT_FILTER_CONFIG_FILE
        self.config: dict = Utils.json_parsor(self.file)
        self.filter_string: list = []
        self.filter_copy_inputs: list = []
        self.filter_copy_outputs: list = []

    def filter_generation(self):
        if "filters" in self.config:
            for filter_name, data in self.config['filters'].items():
                if filter_name == 'copy':
                    self.filter_copy_inputs = [data for data in data.keys()]
                    self.filter_copy_outputs = [data for data in data.values()]
                    self.filter_copy()

                if filter_name == 'scale':
                    for i in data:
                        self.filter_scale(
                            input=i['input'],
                            output=i['output'],
                            resolution=Utils.ensure_list(i['res']),
                            filter=i['filter']
                        )
                if filter_name =='overlay':
                    for item in data:
                        self.overlay(
                            inputs=[item['background'], item['overlay']],
                            x=item['x'],
                            y=item['y']
                        )
                        
        print(";".join(self.filter_string))

    def filter_copy(self):
        filter = ""
        for i in self.filter_copy_inputs:
            if "split" not in filter:
                filter = filter + f"split[{i}]"
            else:
                filter = filter + f"[{i}]"
        self.filter_string.append(filter)


    def filter_scale(self, input, output, resolution: list, *args, **kwargs):
        filter = ""
        if resolution:
            if "scale" not in filter:
                if len(resolution) <= 1:
                    filter = filter + f"[{input}]scale=-1:{resolution[0]}"
                else:    
                    filter = filter + f"[{input}]scale=width={resolution[0]}:height={resolution[1]}"
                for args in kwargs.items():
                    if "gray" in args:
                        filter = filter + f",format=gray"
                    if "hflip" in args:
                        filter = filter + f",hflip"
        filter = filter + f"[{output}]"
        self.filter_string.append(filter)

    def overlay(self, inputs:list, x:str, y:str):
        filter = ""
        for input in inputs:
            filter = filter + f"[{input}]"
        filter = filter + f"overlay=x={x}:y={y}"
        self.filter_string.append(filter)


dummy = MediaOperation()

dummy.filter_generation()




def run_cmd(cmd):
    cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    output, errors = cmd_call.communicate()


def generate_ffmpeg_command(stream_type: str, input_file_path: str, output_file_path: str, duration: str = None):
    """
    Generates an FFmpeg command based on the stream type, input file, output file, and optional duration.

     Parameters
    ----------
    stream_type : Either 'audio' or 'video'.
    input_file_path : Path to the input file.
    output_file_path : Path to the output file.
    duration : Duration in seconds. Defaults to None.

     Returns
    -------
    list: FFmpeg command as a list of strings.

     Examples
    --------
    >>> generate_ffmpeg_command("audio", "demo.mp4", "new_file.mp3", 1)
    >>> generate_ffmpeg_command("video", "demo.mp4", "new_file.mp4", 1)
    """

    if os.path.exists(input_file_path):
        FFMPEG_BIN.extend(["-i", input_file_path])

        if stream_type == "audio":
            FFMPEG_BIN.extend(["-map", "0:a"])

        if stream_type == "video":
            FFMPEG_BIN.extend(["-map", "0:v"])

        if duration:
            FFMPEG_BIN.extend(["-to", str(duration)])

        FFMPEG_BIN.append(output_file_path)
        return FFMPEG_BIN
    else:
        return ["Input file not found !"]


def replace_audio(video_file_path: str, audio_file_path: str, duration: int = 10, output_file_name: str = "out.mp4"):
    """
    Merges an audio file into a video file for a specific duration and saves the output as a new video file.

    Args
    ----
        video_path (str): Path to the video file.
        audio_path (str): Path to the audio file.
        duration (int, optional): Duration of the output video in seconds. Defaults to 10.
        output_file (str, optional): Name of the output video file. Defaults to "output.mp4".

    Returns
    -------
        List[str]: FFmpeg command as a list of strings.

    Examples
    -------
        >>> merge_audio_into_video("video.mp4", "audio.mp3", duration=20, output_file="output_video.mp4")
    """
    audio_stream = 0 # audio stream selector from the audio file
    video_stream = 0 # video stream selector from the video file

    if video_file_path and os.path.exists(video_file_path):
        FFMPEG_BIN.extend(["-i", video_file_path])
    else:
        return ["Invalid video file path !"]
    
    if audio_file_path and os.path.exists(audio_file_path):
        FFMPEG_BIN.extend(["-i", audio_file_path])
        FFMPEG_BIN.extend(["-map", f"0:v:{video_stream}"])
        FFMPEG_BIN.extend(["-map", f"1:a:{audio_stream}"])
    else:
        return ["Invalida video file path !"]

    FFMPEG_BIN.extend(["-to", str(duration), output_file_name])

    return FFMPEG_BIN

def get_file_details(file: str):
    if file:
        return f"ffprobe -v error {file} -show_format -show_streams -print_format json".split()

def _split(output_list: list):
    filter = ""
    for i in output_list:
        if "split" not in filter:
            filter = filter + f"split[{i}]"
        else:
            filter = filter + f"[{i}]"
    return filter

def _scale(input, output, resolution: list, *args):
    filter = ""
    if resolution:
        if "scale" not in filter:
            if len(resolution) <= 1:
                filter = filter + f"[{input}]scale=-1:{resolution[0]}"
            else:    
                filter = filter + f"[{input}]scale=width={resolution[0]}:height={resolution[1]}"
            if "gray" in args:
                filter = filter + f",format=gray"
            if "hflip" in args:
                filter = filter + f",hflip"
    filter = filter + f"[{output}]"
    return filter

def _overlay(inputs:list, x:str, y:str):
    filter = ""
    for input in inputs:
        filter = filter + f"[{input}]"
    filter = filter + f"overlay=x={x}:y={y}"
    return filter

# print(_overlay(["bg_out", "ol_out"], "W-w", "(H-h)/2"))
# print(_scale("bg", "bgout", [1920, 1080], "gray"))
# print(_scale("ol", "ol_out", [480], "hflip"))

def create_filter():
    # split takes parameter like number
    # >>> split[bg][ol]
    # scale takes resolution W & H
    # >>> [bg]scale=width=1920:height=1080,format=gray[bg_out]
    # >>> [ol]scale=-1:480,hflip[ol_out]
    # overlay takes any input and place cordinates
    # >>> [bg_out][ol_out]overlay=x=W-w:y=(H-h)/2
    
    "split[bg][ol];[bg]scale=width=1920:height=1080,format=gray[bg_out];[ol]scale=-1:480,hflip[ol_out];[bg_out][ol_out]overlay=x=W-w:y=(H-h)/2"

def filter1():
    splits_input_labels = ['bg', 'ol']
    splits_output_labels = ['bg_out', 'ol_out']
    print(_split(splits_input_labels))
    print(_scale("bg", "bg_out", [1920, 1080], "gray"))
    print(_scale("ol", "ol_out", [480], "hflip"))    
    print(_overlay(["bg_out", "ol_out"], "W-w", "(H-h)/2"))
    cmd = 'ffmpeg -v error -y -i demo.mp4 -vf "split[bg][ol];[bg]scale=width=1920:height=1080,format=gray[bg_out];[ol]scale=-1:480,hflip[ol_out];[bg_out][ol_out]overlay=x=W-w:y=(H-h)/2" ol.mp4'

def parse_json(file):
    with open(file, 'r') as yaml_in:
        yaml_object = yaml.safe_load(yaml_in)
        return json.dumps(yaml_object)

def read_config_from_file(file):
    filter_config = json.loads(parse_json(file))

