import subprocess, sys, os

# Given a working_dir, alpha_pose_dir, and a video_path, returns the path to the processed video
def process_video(working_dir, alpha_pose_dir, video_path):
    # Check if parameters are valid
    if not os.path.isfile(video_path):
        raise Exception(f"Invalid Video Path: {video_path}")
    if not os.path.isdir(working_dir):
        raise Exception(f"Invalid Working Directory: {working_dir}")
    if not os.path.isdir(alpha_pose_dir) or not alpha_pose_dir[-9:] == "AlphaPose":
        raise Exception(f"Invalid AlphaPose Directory: {alpha_pose_dir}")

    # call ps1 script to process video
    p = subprocess.Popen(["powershell.exe", f"{working_dir}\\call_process_video.ps1 {alpha_pose_dir} {video_path}"], stdout=sys.stdout)
    p.communicate()

    # return path to processed video
    return f"{alpha_pose_dir}\\examples\\res\\AlphaPose_{os.path.basename(video_path)}"


if __name__ == "__main__":
    # set working directory to be able to call ps1 script
    working_dir = os.getcwd()
    
    # set AlphaPose location
    alpha_pose_dir = "C:\\Users\\dunnm10\\VisualStudio\\SE-AlphaPose-Server\\AlphaPose"

    # should make a parameter, or have it wait for a video from the server or smth
    video_path = f"{working_dir}\\TestVideo_Jake.mp4"

    processed_video_path = process_video(working_dir, alpha_pose_dir, video_path)
    print(processed_video_path)
