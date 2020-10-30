import subprocess
import time

def vlc_command(command, vlc):
    """Sends a command to VLC's rc interface and returns the response.
    Note that only single line response are handled correctly.
    """
    # first, read until the prompt: "> "
    c = ""
    while c != ">":
        c = vlc.stdout.read(1)
    # read one extra space
    vlc.stdout.read(1)

    vlc.stdin.write(command + "\n")
    vlc.stdin.flush()
    return vlc.stdout.readline().strip()

def start_vlc(stream_url, output_file):
    # TODO: fix video speed
    transcode = "#transcode{vcodec=h264,acodec=mp4a}:standard{mux=mp4,dst=" + output_file + ",access=file}"
    return subprocess.Popen([
        "vlc",
        stream_url,
        # explicitly close VLC after the transcode operation
        "vlc://quit",
        # interactive cli interface for progress report
        "-I", "rc",
        "--sout", transcode],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        # supress log messages from VLC
        stderr=subprocess.DEVNULL,
        encoding="utf-8")

def log_progress(vlc):
    while True:
        length = int(vlc_command("get_length", vlc))
        if length != -1:
            break
        else:
            time.sleep(0.5)

    while vlc.poll() is None:
        response = vlc_command("get_time", vlc)
        if response == "":
            print("\rempty response", end="", flush=True)
        else:
            passed = int(response)
            print("\r", passed, "/", length, sep="", end="", flush=True)
            time.sleep(1)
    print("\rConversion finished")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        exit(1)
    vlc = start_vlc(stream_url=sys.argv[1], output_file=sys.argv[2])
    log_progress(vlc)
