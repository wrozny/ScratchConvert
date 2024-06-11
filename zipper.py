import os
import zipfile

script_path = os.path.dirname(os.path.realpath(__file__))


def zip_files(file_paths, output):
    with zipfile.ZipFile(output, 'w') as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))


def unzip_files(archive, output_dir):
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Directory {output_dir} doesn't exist!")

    with zipfile.ZipFile(archive, 'r') as zipf:
        zipf.extractall(output_dir)


def build_project(output_name="output"):
    build_dir = os.path.join(script_path, "build")
    project_dir = os.path.join(build_dir, "project")

    if not (os.path.exists(build_dir) and os.path.exists(project_dir)):
        raise FileNotFoundError("Failed to find build files!")

    output_dir = os.path.join(build_dir, "output")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    files = os.listdir(project_dir)
    file_paths = [os.path.join(project_dir, file_name) for file_name in files]

    zip_files(file_paths, os.path.join(output_dir, f"{output_name}.sb3"))
    print(f"Project was successfully built inside {output_dir}")
