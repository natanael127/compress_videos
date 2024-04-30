# ===================== IMPORTS ============================================== #
import os
import sys
import time
import shutil
import tempfile
import pyinputplus

# ===================== CONSTANTS ============================================ #
INPUT_FORMATS = [".mp4", ".mkv", ".avi", ".MOV"]
OUTPUT_FORMAT = ".mp4"
TMP_FILE_PREFIX = "compressed_video_"
ARG_INDEX_PATH = 1
FILE_ERROR_LOG = "video_compression_errors.log"

# ===================== AUXILIARY FUNCTIONS ================================== #
def list_files_by_extension_recursive(directory, extension):
    output_list = []
    list_extensions = []
    if type(extension) == type(""):
        list_extensions = [extension]
    elif type(extension) == type([]):
        list_extensions = extension
    for root, dirs, files in os.walk(directory):
        for file_item in files:
            file_path = os.path.join(root, file_item)
            for ext in list_extensions:
                if file_path.endswith(ext):
                    output_list.append(os.path.join(directory, file_path))
    return output_list

def data_size_string(num_bytes):
    units = ['', 'Ki', 'Mi', 'Gi']
    i = 0
    while abs(num_bytes) >= 1024.0 and i < len(units) - 1:
        num_bytes /= 1024.0
        i += 1
    return f"{num_bytes:,.3f} {units[i]}B"

# ===================== MAIN SCRIPT ========================================== #
# --------------------- Argument validation
input_arg = sys.argv[ARG_INDEX_PATH]
input_arg = os.path.abspath(input_arg)
if os.path.isfile(input_arg):
    list_videos = [input_arg]
elif os.path.isdir(input_arg):
    list_videos = list_files_by_extension_recursive(input_arg, INPUT_FORMATS)
    list_videos.sort()
    for item in list_videos:
        print(item)
    print("\nListed items will be converted")
    yes_or_no = pyinputplus.inputYesNo("Do you accept? [Y/N]: ")
    if yes_or_no == "no":
        exit()
else:
    print("Invalid path")
    exit()
# --------------------- Video conversion
fp, temp_video_path = tempfile.mkstemp(suffix=OUTPUT_FORMAT, prefix=TMP_FILE_PREFIX)
os.close(fp)
os.remove(temp_video_path)
storage_saving = 0
for input_video_path in list_videos:
    output_video_path = os.path.splitext(input_video_path)[0] + OUTPUT_FORMAT
    cmd_result = os.system(f"ffmpeg -i \"{input_video_path}\" -vcodec libx265 -crf 28 \"{temp_video_path}\"")
    if cmd_result == 0: # Success
        storage_saving += os.path.getsize(input_video_path) - os.path.getsize(temp_video_path)
        os.remove(input_video_path)
        shutil.move(temp_video_path, output_video_path)
    else: # Error
        if os.path.isfile(temp_video_path):
            os.remove(temp_video_path)
        error_log = "[" + time.strftime("%Y-%m-%d %H:%M:%S") + "] Returned " + str(cmd_result) + " for file \"" + input_video_path + "\"\n"
        with open(FILE_ERROR_LOG, "a", encoding="utf-8") as fp:
            fp.write(error_log)
print(f"================\nYou have just saved {data_size_string(storage_saving)}")
