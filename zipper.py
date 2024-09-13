import os
import zipfile

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def zip_files(file_paths, output):
    with zipfile.ZipFile(output, 'w') as zip_file:
        for file in file_paths:
            zip_file.write(file, os.path.basename(file))


def unzip_files(archive, output_dir):
    if not (os.path.exists(output_dir) or os.path.exists(archive)):
        raise FileNotFoundError(f"Output directory or archive doesn't exist!")

    with zipfile.ZipFile(archive, 'r') as zip_file:
        zip_file.extractall(output_dir)


def build_sb3(project_dir=None, output_name="output"):
    build_dir = os.path.join(SCRIPT_PATH, "build")
    if project_dir is None:
        project_dir = os.path.join(build_dir, "project")

    if not (os.path.exists(build_dir) and os.path.exists(project_dir)):
        raise NotADirectoryError("Failed to find build directory!")

    output_dir = os.path.join(build_dir, "output")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    files = os.listdir(project_dir)
    file_paths = [os.path.join(project_dir, file_name) for file_name in files]

    zip_files(file_paths, os.path.join(output_dir, f"{output_name}.sb3"))
    print(f"Project was successfully built inside {output_dir}")
